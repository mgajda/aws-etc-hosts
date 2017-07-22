# Generate `/etc/hosts` for AWS hosts

AWS hosts get unpredictable names, and [Valentino Volonghi's](https://twitter.com/dialtone_) script got old,
so I updated it to generate local `/etc/hosts` only.

# Install

```bash
pip install -r requirements.txt
sudo cp /etc/hosts /etc/hosts.default
```
And [configure your `aws` CLI](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)
with `aws configure`.

## Running

```bash
./gen_hosts.py
sudo cp etc_hosts /etc/hosts
```

