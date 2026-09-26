# chat-service

The chat server. For now it's a WebSocket echo server that greets you with the pod and VM it runs
on. It's deployed to the cluster defined in [jzviagin-chat-app/chat-infra](https://github.com/jzviagin-chat-app/chat-infra).

## Run locally

```bash
docker build -t chat-service . && docker run --rm -p 8000:8000 -e INSTANCE=local chat-service
npx wscat -c ws://localhost:8000/ws
```

## How deploys work

`.github/workflows/build-deploy.yml`:

| Event | What happens |
|---|---|
| Pull request | Checks and builds the image (nothing is pushed or deployed) |
| Push to `main` | Builds the Arm image → pushes `ghcr.io/jzviagin-chat-app/chat-service:sha-<commit>` → opens/updates the PR **"Deploy chat-service sha-…"** in chat-infra |

Merging that PR in chat-infra deploys it: Argo CD rolls the new image out within ~3 minutes.
There's always at most one open deploy PR; each new push to main updates it to the latest build.

## One-time setup

### 0. Organization settings (once, as owner of `jzviagin-chat-app`)

Organization → **Settings**:
- **Member privileges → Base permissions: Read**. Members can't push; as owner you still can.
- **Personal access tokens → Settings**: allow access via **fine-grained personal access tokens**
  (the pipeline's token in step 2 needs this).
- **Packages → Package creation**: allow **Public** packages (the cluster pulls the image without
  credentials).

### 1. Commit the code

The `chat-service` repo must be **public** and **empty** (no README or .gitignore created on GitHub).

```bash
cd chat-service                     # the folder from the zip
git init -b main
git remote add origin https://github.com/jzviagin-chat-app/chat-service.git
git add . && git commit -m "Echo server + build/deploy pipeline"
```

Don't push yet: do step 2 first, or the first run's deploy job fails (harmless, just re-run it).

### 2. Give the pipeline permission to open PRs in chat-infra

1. GitHub → your profile → Settings → Developer settings → **Fine-grained personal access tokens** →
   Generate new token.
   - Name: `chat-service-deploy`, expiration: up to you (you'll need to renew it when it expires)
   - **Resource owner: `jzviagin-chat-app`** (the organization, not your user). If the organization
     requires approval for tokens, approve it under Organization → Settings → Personal access tokens →
     Pending requests.
   - Repository access: **Only select repositories → `chat-infra`**
   - Repository permissions: **Contents: Read and write**, **Pull requests: Read and write**
2. Copy the token. In **chat-service** → Settings → Secrets and variables → Actions →
   **New repository secret**: name `INFRA_REPO_TOKEN`, value: the token.

   (You can add the secret right after creating the empty repo, before the first push.)

### 3. Push

```bash
git push -u origin main
```

Watch it under the repo's **Actions** tab. When it's green:

### 4. Make the image public (once)

Organization page → **Packages** → `chat-service` → **Package settings** → **Change visibility → Public**.
The cluster pulls images without credentials, so it must be public.

### 5. Merge the deploy PR

chat-infra → Pull requests → **"Deploy chat-service sha-…"** → Merge.

### 6. Protect main

Settings → Rules → Rulesets → **New branch ruleset** → target: default branch → enable
**Restrict deletions** and **Block force pushes** → Active. With base permission *Read* (step 0) and no
outside collaborators, only you can push.

## Notes

- **Arm builds:** the workflow uses GitHub's `ubuntu-24.04-arm` runners (free for public repos), so
  the image is native arm64 like the Oracle Ampere VMs.
- **The token** acts as you, with access to chat-infra only. The workflow only uses it to open a
  PR, so your merge stays the deploy step. It's still a write credential: it lives only in the
  repo secret, and you should revoke it on GitHub if it ever leaks.
