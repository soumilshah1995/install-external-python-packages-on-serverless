# serverless-gitlab-ci

## Description

Basic nodejs CI setup for gitlab's CI service. This configuration can be used with their free tier usage or their self-hosted solution. This lets devs collaborate on simple serverless projects with automatic deployment on merge. This also tags each merge to an environment for automatic tracking in the `CI / CD > Environments` tab.

This setup also includes a dummy test command that will run on all branches. Ideally this would be replaced with real tests to enable a true CI experience.

## Usage

Navigate to [gitlab.com](https://gitlab.com/) and create a new repo.

Then go to `settings > CI / CD`  and expand the `Secret Variables` section. Click `Add New Variable` and add

```yml
Key: AWS_ACCESS_KEY_ID
Value: YOUR_ACCESS_KEY
Protected: ✓

Key: AWS_SECRET_ACCESS_KEY
Value: YOUR_SECRET_VALUE
Protected: ✓
```

Enabling protected limits these variables to specific branches that we define (eg: staging and master, since they'll be the only ones that deploy anything). See `settings > Repository` and expand protected branches to set the access (Can enable user, or group level access).

Next up, template this repo with
```bash
serverless create --template-url https://github.com/bvincent1/serverless-gitlab-ci/master --path myService
```

And set the remote to the gitlab url

```bash
cd myService
git init # init repo if needed
git remote add origin git@gitlab.com:username/myrepo.git
git add -A
git commit -a -m 'Init repo from template'
git push -u origin master
```

This should create the repo and automatically create the ci pipeline.

## Special Notes

- Ideally you could just use AWS IAM to create a new admin user and use those keys and not your own. This lets you track usage and keeps your keys separate. Best practice even suggests you rotate keys regularly, but thats a whole different story.

- This project uses `yarn` as the node_modules install tool. This can be easily changed by modifiying the `.gitlab-ci.yml` file and changing the `yarn` command to `npm`.

- Additional Gitlab CI example [RestfullSheets](https://gitlab.com/dotslashsolve/RestfulSheets/)
