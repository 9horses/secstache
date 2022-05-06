"""
    secstache - fill mustache with secrets
"""
import sys
import argparse
import json
import boto3
import pystache
import botocore


def load_data_asm(asm):
    """
    Parse Amazon Secret Manager entry as secret dict.
    Takes `asm_key` as input which is interpreted as `key_id:key_ver`
    The version information is optional.
    """
    sm = boto3.client('secretsmanager')
    kv_dict = {}
    for asm_key in asm:
        asm_key_parts = asm_key.split(':')
        try:
            if len(asm_key_parts) > 1:
                resp = sm.get_secret_value(SecretId=asm_key_parts[0],
                                           VersionId=asm_key_parts[1])
            else:
                resp = sm.get_secret_value(SecretId=asm_key_parts[0])
            kv_dict.update(json.loads(resp.get('SecretString')))
        except botocore.exceptions.ClientError as err:
            print(f"Failed to load secrets from asm key {asm_key}: {str(err)}")
            next
    return kv_dict


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Fill mustache template(s) with secrets from secret store(s).'
        ),
        epilog=('EXAMPLE:\n' +
                '\tCreate db.conf from db.conf.mustache using secrets in ' +
                'AWS Secret Manager under "prod/db"\n' +
                '\n' +
                '\t\tsecstache --asm prod/db db.conf.mustache'),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('files', metavar='file1.mustache', type=str, nargs='*',
                        help='mustache files to process')
    parser.add_argument('--asm', metavar='key', action='append',
                        help='AWS Secret Manager key')
    parser.add_argument('--strict', action='store_true',
                        help='fail if a tag key is not found')

    args = parser.parse_args()

    data_dict = {}

    if args.asm:
        data_dict.update(load_data_asm(args.asm))

    if not data_dict:
        sys.exit("Can not process any templates: No secrets were loaded.")

    missing_tags = 'strict' if args.strict else 'ignore'
    renderer = pystache.Renderer(missing_tags=missing_tags)
    if len(args.files) == 0:
        with sys.stdin as f:
            template = f.read()
        try:
            rendered = renderer.render(template, data_dict)
            print(rendered)
        except pystache.context.KeyNotFoundError as err:
            sys.exit(f"Failed to render template: {str(err)}")
    else:
        for fn in args.files:
            if fn.lower().endswith('.mustache'):
                with open(fn, 'r') as f_in:
                    template = f_in.read()
                try:
                    rendered = renderer.render(template, data_dict)
                    fn_rendered = fn[0:-len('.mustache')]
                    with open(fn_rendered, 'w') as f_out:
                        print(rendered, file=f_out)
                    print(f"Rendered {fn} to {fn_rendered}")
                except pystache.context.KeyNotFoundError as err:
                    print(f"Failed to render {fn}: {str(err)}",
                          file=sys.stderr)
            else:
                print(f"{fn} does not have extension .mustache - ignored")


if __name__ == "__main__":
    main()
