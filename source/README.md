# Código-fonte do gerador do site RIMA studio

Esta pasta guarda o **sistema que gera** o site estático publicado neste repositório (`dist/` → raiz do repo). Sem isto, só existe o HTML/CSS já gerado — qualquer alteração de conteúdo teria de ser feita à mão, ficheiro a ficheiro.

## Estrutura

- `build.py` — gerador do site (Python 3, sem dependências externas: usa só `json`, `os`, `shutil`, `html`)
- `data/site.json` — todos os textos do site, em PT e EN (hero, serviços, secção "O que fazemos", missão, estúdio, lab, etc.)
- `data/projects.json` — os 23 projetos do portefólio (título, tags, imagens, categorias)
- `web/` — todas as imagens já convertidas para `.webp` (qualidade 86), prontas a copiar para `dist/images/`. Nomes de ficheiro seguem o padrão dos hashes originais do Wix (`e46b83_<hash>~mv2.webp`)

## Como gerar o site

```bash
cd source
python3 build.py
```

Isto cria/atualiza uma pasta `dist/` ao lado de `build.py`, com todas as páginas HTML (PT + `en/`), CSS, JS e imagens. O conteúdo de `dist/` é depois copiado para a raiz deste repositório (é isso que o Cloudflare Workers publica).

## Como adicionar/trocar uma imagem

1. Descarregar/preparar a imagem
2. Converter para `.webp` (recomenda-se qualidade ~86, largura máxima ~1000–1600px conforme o uso):
   ```python
   from PIL import Image, ImageOps
   im = Image.open("origem.jpg")
   im = ImageOps.exif_transpose(im)
   im.thumbnail((1600, 1600), Image.LANCZOS)
   im.save("web/nome-do-ficheiro.webp", "WEBP", quality=86, method=6)
   ```
   (precisa de `pip install Pillow`)
3. Colocar o `.webp` em `web/`
4. Referenciar o nome do ficheiro em `data/projects.json` (campo `images`) ou, para capas da grelha, no dicionário `PROJECT_COVERS` no topo de `build.py`
5. Correr `python3 build.py` outra vez

## Notas importantes para quem continuar este trabalho

- **Capas dos projetos na grelha (`PROJECT_COVERS` em `build.py`):** no site Wix original, a imagem de capa de cada projeto na grelha do portefólio é um ficheiro dedicado, diferente das imagens dentro da página do próprio projeto. 18 de 23 projetos já têm a capa certa mapeada; 5 ficam com fallback (primeira imagem do projeto) por não ter sido possível confirmar a capa certa com confiança.
- **Sistema tipográfico:** corpo de texto em "Old Standard TT"; títulos de secção, CTAs e títulos de serviços em "Karla" bold. Exceção confirmada contra o site original: o título do hero e os "eyebrows"/labels usam "Karmilla" Bold, não Karla — não mudar isso sem voltar a verificar contra o Wix original.
- **`dist/css/style.css` não é gerado pelo `build.py`** — é um ficheiro estático editado diretamente (só é copiado/referenciado via `<link>`, nunca reescrito pelo script).
- **Secções com fundo dependente de contexto:** os logótipos de clientes são brancos (pensados para fundo escuro) — qualquer secção que os mostre tem de usar a classe `band-dark`, senão ficam invisíveis num fundo claro.

## Deploy

Ver o documento `RIMA_migracao_site_contexto.md` (entregue ao Ricardo em separado) para o fluxo completo de deploy — resumidamente: gerar `dist/`, copiar o conteúdo para a raiz do repositório, `git add` + `git commit`, e o Ricardo corre `git push` (é o único passo que precisa das credenciais dele).
