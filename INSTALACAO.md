# Instalação do perfil no GitHub

1. Abra o repositório `https://github.com/samaelsimoes/samaelsimoes` (deve ser **público** e ter o mesmo nome do seu usuário).
2. Envie o `README.md`, a pasta `assets`, a pasta `scripts` e `.github/workflows` preservando as pastas.
3. No repositório, abra **Actions** → **Atualizar métricas do perfil** → **Run workflow**.
4. Aguarde o workflow terminar. Ele gera quatro SVGs com seus dados verdadeiros e salva os arquivos em `assets/`.
5. Depois disso, os gráficos serão atualizados automaticamente uma vez ao dia.

## Observações importantes
- Os arquivos SVG iniciais são espaços reservados; depois da primeira execução serão substituídos pelos gráficos verdadeiros.
- Se o GitHub bloquear o push automático, vá a **Settings → Actions → General → Workflow permissions** e selecione **Read and write permissions**, e rode novamente.
- Métricas são calculadas com a **API oficial GitHub GraphQL**. Contribuições em repositórios corporativos privados podem não ser visíveis; elas não são inventadas nem estimadas.
- O gráfico mensal representa **contribuições registradas**, não apenas commits. O card de visão geral mostra **commits** separadamente.
- Os cartões de linguagens dependem de um serviço externo e podem ficar temporariamente indisponíveis. O restante das estatísticas usa arquivos SVG armazenados dentro do próprio repositório.
- Verifique que seu e-mail e LinkedIn continuam corretos antes de publicar.
