# ship-it-properly

A small CI/CD project: every code change is tested automatically, and every merge to `main` is deployed to AWS Lambda with no manual steps, no stored AWS passwords, and a one-command rollback.

The app itself is deliberately simple. The pipeline around it is the point.

## What the app does

A file checker, the kind of validation a print or upload workflow needs before accepting a file. It accepts only `.pdf`, `.png`, `.jpg` and `.jpeg` files up to 5 MB, and says why when it rejects one.

```
{"filename": "menu.pdf",  "size_bytes": 2000}      ->  {"accepted": true,  "reason": "ok"}
{"filename": "virus.exe", "size_bytes": 2000}      ->  {"accepted": false, "reason": "file type not allowed"}
```

It runs on AWS Lambda (Python 3.12), so nothing costs money while it sits idle.

## The pipeline

```mermaid
flowchart LR
    A[Pull request] --> B[Run tests]
    B -->|pass| C[Merge to main]
    C --> D[Run tests again]
    D --> E[Get temporary AWS access via OIDC]
    E --> F[Update Lambda code]
    F --> G[Publish numbered version]
    G --> H{Smoke test the new version}
    H -->|pass| I[Move live alias to new version]
    H -->|fail| J[Stop - live stays on the old version]
```

| Stage | What happens | Why it matters |
|---|---|---|
| Pull request | Tests run, nothing is deployed | Broken code is caught before it reaches `main` |
| Merge to `main` | Tests run again, then the deploy job starts | Only tested code is ever deployed |
| OIDC login | GitHub gets short-lived AWS credentials | No access keys are stored anywhere |
| Publish version | A frozen, numbered copy of the function is created | Every release can be restored |
| Smoke test | The new version is called before anyone uses it | A bad deploy is caught first |
| Move `live` alias | Only happens if the smoke test passed | Users stay on the old version if it fails |

## Security: no stored credentials

The workflow does not use AWS access keys. GitHub presents a short-lived identity token (OIDC) and AWS exchanges it for temporary credentials that expire within the hour.

The deploy role is locked down:

- It trusts only the `main` branch of this one repository.
- It can only touch one Lambda function (`file-checker`), with only the permissions the pipeline needs.

## Rollback

The `live` alias is a pointer to a numbered version. If a bad version ever gets through, rollback means moving the pointer back, which takes seconds and needs no new code:

```
aws lambda update-alias --function-name file-checker --name live --function-version <previous-version>
```

## Run the tests locally

```
pip install -r requirements.txt
pytest
```

## Project layout

```
handler.py                  the file checker and the Lambda entry point
test_handler.py             tests (run on every pull request and every push to main)
requirements.txt            test dependencies
event.json                  sample input for invoking the function
trust-policy.json           lets Lambda assume its execution role
.github/workflows/ci.yml    the pipeline
```

## What I learned building it

- **OIDC trust failures are hard to read.** The deploy kept failing with "Not authorized to perform sts:AssumeRoleWithWebIdentity" even though the role looked correct. I added a temporary step to the workflow that decoded the identity token GitHub was actually sending. In this repo, the token's subject included numeric user and repository IDs, so my role's trust rule (which used plain names) never matched. Fixing the trust policy resolved it.
- **Test the new version before switching users to it.** Publishing a version and smoke-testing it before moving the alias means a failed deploy never reaches live traffic.
- **Least privilege takes a few extra minutes and is worth it.** The deploy role can do almost nothing outside this one function.

## Limitations and next steps

- The AWS resources (Lambda function, IAM roles, OIDC provider) were created with AWS CLI commands, not infrastructure as code.
- Next: define the infrastructure in Terraform, add a staging environment with a manual approval gate before production, and add automatic rollback when a CloudWatch alarm fires.
