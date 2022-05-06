# secstache

Fill [mustache](https://mustache.github.io/) template(s) with secrets from secret store(s).

## Installation
```
pip install secstache
```

## Usage
```
$ secstache -h
usage: secstache [-h] [--asm key] [--strict] [file1.mustache ...]

Fill mustache template(s) with secrets from secret store(s).

positional arguments:
  file1.mustache  mustache files to process

optional arguments:
  -h, --help      show this help message and exit
  --asm key       AWS Secret Manager key
  --strict        fail if a tag key is not found

EXAMPLE:
	Create db.conf from db.conf.mustache using secrets in AWS Secret Manager under "prod/db"

		secstache --asm prod/db db.conf.mustache
```

## Example

Say, you have a secret stored in secrets manager under the name of `prod/db` with the SecretString set to:
```
{
  "DB_USER": "foo_user",
  "DB_PASS": "foo_pass"
}
```
You can create a mustache file like this:
```
$ cat db.conf.mustache
DB_NAME = foo_db
DB_USER = {{DB_USER}}
DB_PASS = {{DB_PASS}}
```
and run `secstache` this way:
```
$ secstache --asm prod/db db.conf.mustache
Rendered db.conf.mustache to db.conf
```
This creates the db.conf file that looks like this:
```
$ cat db.conf
DB_NAME = foo_db
DB_USER = foo_user
DB_PASS = foo_pass
```

## Supported secret stores

### AWS Secrets Manager
Load secrets from [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) via `--asm key` option. Note that your environment must be configured so as to support `boto3`. (I.e., you must be able to run `aws` successfully in your environment.)

### Other secret stores
PR's welcome! :grin:

