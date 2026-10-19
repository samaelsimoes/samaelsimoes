# Instalação / Installation

1. Copie `README.md` para a raiz do repositório público de perfil `samaelsimoes/samaelsimoes`.
2. Copie a pasta `scripts` e o workflow `.github/workflows/update-profile-charts.yml` mantendo os caminhos.
3. No GitHub: `Settings > Actions > General > Workflow permissions`, marque `Read and write permissions` (se essa configuração estiver disponível para o repositório).
4. Acesse `Actions > Update bilingual profile contribution charts > Run workflow`.
5. Depois que terminar, confira `assets/contribution-calendar.svg`, `assets/monthly-activity.svg` e `assets/contribution-breakdown.svg` no repositório.
6. Se algum gráfico não aparecer, verifique os logs do workflow. A execução diária usa `GITHUB_TOKEN`, sem precisar cadastrar um token privado manualmente.

## Observações importantes

- Os SVGs não existem até o primeiro workflow terminar com sucesso. O README mostrará imagens quebradas antes disso.
- O GitHub pode diferenciar contribuições visíveis no navegador das visíveis ao token do workflow, especialmente para repositórios privados ou corporativos.
- O gráfico de distribuição por commits/PRs/issues/reviews não equivale exatamente ao widget nativo Activity Overview.
- Se você já tem outro workflow com o mesmo objetivo, pode manter ambos, mas haverá atualizações independentes e arquivos SVG diferentes.
- Como alternativa, ative `Include private contributions on my profile` nas configurações do GitHub para exibir totais privados de maneira anônima no seu perfil. Isso não garante que uma Action consiga acessar esses dados.
