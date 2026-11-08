#!/usr/bin/env python3
"""Prova integrada: locução ElevenLabs com animação quadro-a-quadro e legendas por cena."""
import json
import math
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from teste_animacao import FPS, H, OUT, W, frame

VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
LINES = [
    "O som sai da caixa acústica e pode alcançar o microfone.",
    "O microfone capta esse som e o envia novamente para amplificação.",
    "Quando esse ciclo se repete, surge aquele apito chamado microfonia.",
    "Para controlar, ajuste o ganho e posicione corretamente as caixas.",
]
PAUSE = 0.35


def run(*command):
    subprocess.run([str(x) for x in command], check=True)


def duration(filename):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(filename)],
        text=True).strip())


def synth(index, text, key):
    filename = OUT / f"voz-sincronizada-{index}.mp3"
    payload = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "output_format": "mp3_44100_128",
    }, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID,
        data=payload,
        headers={"Content-Type": "application/json", "xi-api-key": key,
                 "Accept": "audio/mpeg"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            filename.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        # Não expor a chave nem dados privados contidos na resposta da API.
        raise RuntimeError(f"ElevenLabs retornou HTTP {exc.code} na cena {index}") from None
    if filename.stat().st_size < 1000:
        raise RuntimeError("Resposta de áudio inválida.")
    return filename


def main():
    secret = os.environ.get("ELEVENLABS_API_KEY")
    if not secret:
        raise RuntimeError("O segredo ELEVENLABS_API_KEY não está configurado.")
    OUT.mkdir(exist_ok=True)
    audio = [synth(i, line, secret) for i, line in enumerate(LINES)]
    durations = [duration(a) + PAUSE for a in audio]
    # Concatenar trechos e adicionar pequenas pausas, preservando a duração de cada cena.
    filter_parts = []
    for i, dur in enumerate(durations):
        filter_parts.append(
            f"[{i}:a]aresample=48000,apad=pad_dur={PAUSE},"
            f"atrim=duration={dur:.6f},asetpts=PTS-STARTPTS[a{i}]"
        )
    filter_parts.append("".join(f"[a{i}]" for i in range(len(audio))) +
                        f"concat=n={len(audio)}:v=0:a=1[a]")
    combined = OUT / "narracao-sincronizada.wav"
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        *[arg for a in audio for arg in ("-i", str(a))],
        "-filter_complex", ";".join(filter_parts),
        "-map", "[a]", "-c:a", "pcm_s16le", str(combined))
    total_frames = [max(1, math.ceil(dur * FPS)) for dur in durations]
    dest = OUT / "Xandao-Teste-Voz-Animacao.mp4"
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "-",
        "-i", str(combined), "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", str(dest),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for i, count in enumerate(total_frames):
            for n in range(count):
                # Tempo visual normalizado para cada bloco de narração, sem cortes no meio da frase.
                virtual_time = i * 3 + (n / count) * 3
                process.stdin.write(frame(int(virtual_time * FPS)).tobytes())
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("FFmpeg não conseguiu montar o vídeo sincronizado.")
    finally:
        if process.poll() is None:
            process.kill()
    run("ffprobe", "-v", "error", "-show_entries", "format=duration,size",
        "-of", "default=noprint_wrappers=1", str(dest))
    print("MP4 sincronizado gerado:", dest)


if __name__ == "__main__":
    main()
