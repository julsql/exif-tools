---
name: release
description: >
  Publie une nouvelle version d'ExifTools : met à jour version.txt (numéro
  passé en argument, sinon incrémente le patch de 1), propage via
  bump_version.py, commit, crée le tag de version puis la release GitHub.
  Déclenche dès que l'utilisateur dit "release", "publie une version",
  "sors une nouvelle version", "fais une release", ou utilise le slash
  `/release` (avec ou sans numéro de version).
---

# Release

Automatise la publication d'une nouvelle version d'ExifTools. Le numéro de
version vit dans `version.txt` et est propagé dans tout le repo par
`bump_version.py`. Le tag et la release GitHub suivent une nomenclature
stricte qu'il faut respecter à la lettre.

## Arguments

- **Avec argument** (`/release 2.1.0`) : utilise ce numéro tel quel.
- **Sans argument** (`/release`) : incrémente le **patch** de 1 par rapport à
  `version.txt` (ex: `2.0.5` → `2.0.6`).

## Conventions du projet (à respecter scrupuleusement)

- **`version.txt`** : contient uniquement le numéro `X.Y.Z`, **sans saut de
  ligne final**. Ne pas en ajouter.
- **Tag** : le numéro nu `X.Y.Z`, **sans préfixe `v`** (ex: `2.0.5`).
- **Titre de la release** : `Version X.Y.Z`.
- **Corps de la release** : voir le format ci-dessous.

### Format du corps de release

```
VERSION X.Y.Z
<résumé en français, une ou plusieurs lignes, décrivant l'essentiel de la version>

🌟 Ajout de feature
- <description en français> (<SHA complet du commit>).
- ...

🐛 Correction de bug
- <description en français> (<SHA complet du commit>).
- ...
```

Règles du corps :
- Première ligne toujours `VERSION X.Y.Z` (majuscules).
- Puis un résumé libre en français (les versions majeures ou avec breaking
  change commencent souvent par `ATTENTION : ...`).
- Une ligne vide, puis les sections par catégorie. N'inclure que les sections
  pertinentes. Catégories observées, dans cet ordre :
  - `🛠️ Reprise de feature manquantes` — features réintroduites/correctifs de régression
  - `🌟 Ajout de feature` — nouvelles fonctionnalités (commits `feat`)
  - `🐛 Correction de bug` — corrections (commits `fix`)
- Chaque puce : `- ` + description en français + ` (` + **SHA complet** du
  commit + `).` (point final).
- Le français est la langue du corps de release (≠ messages de commit en
  anglais).

## Workflow

1. **Déterminer la nouvelle version**
   - Lire `version.txt`.
   - Si un argument est fourni, c'est la nouvelle version (valider le format
     `X.Y.Z`). Sinon, incrémenter le patch de 1.
   - Vérifier que le tag n'existe pas déjà : `git tag | grep -x "<version>"`.
     S'il existe, s'arrêter et le signaler.

2. **Mettre à jour `version.txt`** avec la nouvelle version, sans saut de ligne
   final (`printf '%s' "X.Y.Z" > version.txt`).

3. **Propager** : `python3 bump_version.py` (lit `version.txt` et met à jour
   README, `editor/main_window.py`, `editor/app.py` et les scripts d'install).

4. **Préparer le corps de release** : lister les commits depuis le dernier tag
   pour catégoriser le changelog.
   - Dernier tag : `git describe --tags --abbrev=0` (ou le plus récent de
     `git tag --sort=-creatordate`).
   - `git log <dernier_tag>..HEAD --pretty=format:'%H %s'` pour récupérer
     SHA complet + sujet.
   - Classer chaque commit dans la bonne catégorie (`feat:` → 🌟,
     `fix:` → 🐛, etc.), reformuler en français orienté utilisateur, et
     terminer chaque puce par le SHA complet entre parenthèses.
   - Rédiger un résumé d'intro en français.
   - **Faire valider le corps de release à l'utilisateur avant de publier.**

5. **Commit** : stager `version.txt` et tous les fichiers modifiés par
   `bump_version.py`, puis committer en anglais (Conventional Commits) :
   `chore(release): bump version to X.Y.Z`.

6. **Pousser le commit** : `git push`.

7. **Créer le tag et le pousser** :
   ```
   git tag X.Y.Z
   git push origin X.Y.Z
   ```

8. **Créer la release GitHub** avec le corps validé (HEREDOC pour préserver le
   formatage et les emojis) :
   ```
   gh release create X.Y.Z --title "Version X.Y.Z" --notes "$(cat <<'EOF'
   VERSION X.Y.Z
   ...
   EOF
   )"
   ```
   Ne **pas** attacher d'assets manuellement : le workflow
   `.github/workflows/release-build.yml` builde et publie automatiquement les
   installateurs (.dmg / .exe) au déclencheur `release: published`.

9. **Confirmer** : afficher l'URL de la release (`gh release view X.Y.Z --web`
   n'est pas nécessaire, donner juste l'URL retournée par `gh release create`).

## Règles importantes

- **Ne jamais publier sans validation du corps de release** par l'utilisateur —
  le changelog est rédigé à la main à partir des commits, il faut le relire.
- **Format de tag sans `v`** — vérifier sur `git tag` si un doute.
- **Pas de saut de ligne dans `version.txt`**.
- **Messages de commit en anglais, corps de release en français.**
- Si le `git log` depuis le dernier tag est vide, signaler qu'il n'y a rien à
  release plutôt que de publier une version vide.
- Si l'arbre de travail est sale avant de commencer, le signaler (des modifs
  non liées seraient embarquées dans le commit de release).
