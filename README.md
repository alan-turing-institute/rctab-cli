# RCTab CLI

A CLI for interacting with the [RCTab API](https://github.com/alan-turing-institute/rctab-api).

## What it does

- Add subscriptions to the Research Compute Billing System.
- **Approve credits** for a subscription.
  Approved credits are ring fenced for a subscription but can not be spent until they are allocated.
- **Allocate credits** (that have already been approved) to a subscription.
  They can now be spent.
- Check all the approvals and allocations made for a subscription.
- Get a summary of all the approvals, allocations and costs for all subscriptions.

## What it doesn't do (yet)

- Create subscriptions on Azure.
  They must be created through the Azure portal and then added to the billing system.
- Add users to a subscription.
  Do this through the Azure portal.
  The billing system will then pick them up and you will see the changes on the CLI.

## Install

### User install

```bash
pip install git+https://github.com/alan-turing-institute/rctab-cli
```

### Developer Install

To get started install [Poetry](https://python-poetry.org/docs/).

Then install dependencies and activate a Poetry shell, which we will assume is active for the rest of the document

```bash
poetry install
poetry shell
```

## Usage

### Get help

See documentation and cmds with

```bash
rctab --help
```

Use this to get more information about the commands below

```bash
rctab <cmd> --help
```

Check you are using the most up to date versions of the CLI and API:

```bash
rctab --version
```

### Configuration


When you set up the [RCTab API](https://github.com/alan-turing-institute/rctab-api), you should have [registered an app with the Microsoft identity platform](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app).
You will need to set environment variables with the Active Directory Tenant ID and Client ID from that set up process.
You can either do this in the shell, see below, or by adding them to a file named `.auth.env`.

```shell
export CLIENT_ID="00000000-0000-0000-0000-000000000009"
export TENANT_ID="00000000-0000-0000-0000-00000000000a"
```

You will need to set environment variables with the web address and port of your Research Compute API server.
You can either do this in the shell or by adding them to a file named `.env`.

If you are developing locally, this might look like this

```bash
export BASE_URL="http://localhost"
export PORT=8000
```

and if you are interacting with a production deployment, it might look like

```bash
export BASE_URL="https://my-rctab.azurewebsites.net"
export PORT=443
```
Make sure that `BASE_URL` has no trailing `/`.
See [config.py](./rctab_cli/config.py) for more

### Sign in using your AD credentials and request access

Request access to the API with

```bash
rctab request-access
```

Once you've done this, the `is_admin` flag will need to be set in the RCTab database for you to have CLI access.

### Managing Subscriptions

All subcommands for managing subscriptions start with `rctab sub`

#### Summary of all subscriptions

To view a summary of all subscriptions run

```bash
rctab sub summary
```

You can filter a single subscription

```bash
rctab sub summary --subscription-id {SUBSCRIPTION_ID}
```

#### See all approvals and allocations

You can get a detailed information about all the approvals (credits ring fenced for a subscription - these have an expiry date), and allocations (credits ready to spend on a subscription).
The `summary` command provides a summary of these.

```bash
rctab sub approvals --subscription-id {SUBSCRIPTION_ID}
```

```bash
rctab sub allocations --subscription-id {SUBSCRIPTION_ID}
```

#### Add a new subscription

You need to create the subscription on the Azure portal and ensure it is placed in the `EA` management group - otherwise the billing system cannot manage the subscription. Once done, you can add the subscription on to the billing system.

Run

```bash
rctab sub add
```

If no arguments are provided the CLI will interactively ask you for all the information it requires.
You can also pass these as arguments.
To find out what these are run

```bash
rctab sub add --help
```

You should then check the subscriptions details using the summary command above.

#### Change persistence

By default subscriptions are set to expire when they run out of credits or they expire.
However, you can change the 'persistence' of a subscription such that it will always be on.

```bash
rctab sub set-persistence --subscription-id {SUBSCRIPTION_ID} --persistent
```

or to change back

```bash
rctab sub set-persistence --subscription-id {SUBSCRIPTION_ID} --no-persistent
```

#### Approve additional credits

You can approve more credits on a subscription

```bash
rctab sub approve --subscription-id  {SUBSCRIPTION_ID} --ticket {HELPDESK_TICKET} --amount {GBP} --date-to {EXPIRY_DATE} --allocate
```

The {EXPIRY_DATE} is the day the subscription will expire, not the last day it is usable.
For example the date `2020-04-01` means the subscription will last work on the `2022-03-31`.

The `--allocate` flag will allocate the full approval at the same time.
If you omit this you can allocate a smaller amount of the approval using the allocate command.

You can set the approval starting date to be in the future with `--date-from {FUTURE-DATE}`.

#### Remove approved credits

You can remove credits by making a negative approval.
You must make sure you deallocate credits first and can only remove credits that haven't yet been spent.

#### Allocate credits

If you want to approve and allocate credits at the same time use the approve command with the  `--allocate` flag.
If you would like to allocate credits that have already been approved use

```bash
rctab sub allocate --subscription-id  {SUBSCRIPTION_ID} --ticket {HELPDESK_TICKET} --amount {GBP}
```

#### Deallocate credits

To remove credits use the above command with a negative allocation.
You may then want to remove the approval for the credits with a negative approval.

#### Cost recovery process

It may be desirable to charge a subscription's Azure usage to a particular project or department, which you can do with a two-step process.
First, we specify the subscription ID, the monetary amount & timeframe and the finance code for the project or department who will be billed for the spending:

```bash
rctab sub finance create --subscription-id '000-000-000-001' --date-from '2022-01' --date-to '2022-04' --amount 7000 --finance-code 'F-ENG-001'
```

This will create a Finance entry in the RCTab database, which means that up to £7,000 of subscription 000-000-000-001's spending between Jan and April 2022 (inclusive) will be charged to finance code F-ENG-001.

Here, `finance` is a separate command for handling finance table operations. You can view the details of these commands by running:

```bash
rctab sub finance --help
```

The second part of the process is to calculate recoverable costs for all subscriptions for previous months (in order)

```bash
$ rctab sub cost-recovery --month 2022-01
...
$ rctab sub cost-recovery --month 2022-02
...
```

These must be run in order and should be run exactly once for each previous month (you can start on any month before the earliest Finance entry start date).

If you need to modify a Finance entry, you can list the entries for a subscription with

```bash
$ rctab sub finance list --subscription-id  000-000-000-001
[{...'id': 59}]
```

where we see that our subscription has one Finance entry with an ID of 59.
We can then use this Finance ID to update the Finance entry, as long as it would not conflict with cost already recovered:

```bash
rctab sub finance update --amount 6000 --finance-id 59 --subscription-id '000-000-000-001'
```
