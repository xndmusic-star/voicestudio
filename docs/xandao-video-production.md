# Xandão Video Studio — integração de produção

## Repositório central
Este repositório (xndmusic-star/voicestudio) é o ponto de orquestração da produção de vídeos educativos em português brasileiro.

## Serviços e responsabilidades
- VoiceStudio: gerenciamento de projetos, locução, edição de voz e transcrição.
- ElevenLabs: narração principal aprovada; **não armazenar chaves no código**.
- OpenMontage (xndmusic-star/openmontage): pesquisa, storyboard e composição de vídeo.
- FFmpeg: montagem, mixagem final, efeitos e renderização MP4.

## Meta da produção 01
Tema: microfonia no áudio ao vivo.
Formato: vídeo educativo completo (aprox. 3–5 minutos), horizontal 16:9 como master e recortes 9:16.
Requisitos: demonstrações visuais de realimentação, diagramas dinâmicos, medidores e espectrogramas animados, exemplos de posicionamento, títulos e legendas sincronizadas, efeitos de transição e trilha musical discreta.
Não substituir animação real por slides estáticos com zoom.

## Plano de execução
1. Criar roteiro e storyboard com duração por cena.
2. Gerar a voz de cada trecho em ElevenLabs com a voz aprovada, confirmar créditos e permissões. O MP3 aprovado anterior só é adequado para o vídeo curto.
3. Gerar elementos animados com fontes permissivas, renderizar cenas e manter projeto reprodutível.
4. Sincronizar legendas e animações com a narração.
5. Compor trilha, efeitos sonoros e master de áudio.
6. Renderizar MP4 e validar resolução, duração, sincronismo e artefato.
7. Publicar o MP4 como artefato do GitHub Actions.

## Segurança e pré-requisitos
A variável `ELEVENLABS_API_KEY` já foi configurada no repositório `xndmusic-star/elevenlabs-js`, **mas segredos do GitHub Actions não são compartilhados entre repositórios**. Para execução diretamente neste repositório, é necessário adicionar um segredo homônimo em Settings → Secrets and variables → Actions, ou criar uma arquitetura de chamada controlada.

A execução 3 do fluxo antigo retornou HTTP 401 da ElevenLabs; antes de gerar locuções longas, verificar o motivo sem divulgar a chave nos logs. Caso persista, não trocar a voz silenciosamente: solicitar aprovação para alternativa.

## Preservação
Não alterar o código central e aplicativos originais do VoiceStudio. Manter toda a integração do projeto Xandão em diretórios dedicados e workflows próprios.
