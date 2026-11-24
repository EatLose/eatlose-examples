# EatLose diary examples

Count a week’s confirmed meals and calculate the average estimated protein on days with a known total. The same calculation works on the bundled sample and a diary shared by its owner. [简体中文](README.zh-CN.md)

## Try the fictional diary

From the repository root, run this with Python 3. The sample runs offline with the standard library.

```sh
python3 examples/weekly_recap.py
```

The sample has **14 confirmed meals across 6 logged days**, with **71.3 g of estimated protein per logged day with a known value**. The program prints JSON a developer can use in a tool or an assistant. To try the calculation in a chat, copy the question and data from the website. [Try the weekly recap](https://eatlose.com/agents/#try)

You can also fetch the same fictional data directly.

```sh
curl -fsS https://eatlose.com/agents/sample-week.json
```

## Try an authorised diary

1. In EatLose, open **Profile → Connect an agent**. Choose whether to include weight you logged, then tap **Allow and copy instruction**.
2. Run `python3 examples/weekly_recap.py --live`. At the hidden prompt, paste just the token that follows `Bearer` in the copied instruction. The program reads the summary once from EatLose and prints the recap locally.
3. To stop sharing, open **Connect an agent → Disconnect agent**. A grant lasts up to 30 days. Issuing a new one immediately replaces the previous one.

For an unattended integration, load the user’s diary token into `EATLOSE_DIARY_TOKEN` from your secret store. Keep each token bound to the user who granted it. Keep tokens and real diary responses out of public repositories, examples, issue reports and logs.

## Call the API yourself

Use this read-only GET with the token in an HTTP header. The example assumes `EATLOSE_DIARY_TOKEN` is set locally.

```sh
curl -fsS -H "Authorization: Bearer ${EATLOSE_DIARY_TOKEN:?Set the diary token first}" \
  https://kgnnsvcrxefvavdyvakk.supabase.co/functions/v1/agent-diary
```

- The response covers seven local dates, including today. Each row counts confirmed, synced meals. An absent date means no meals were logged and synced for it. A person can log only part of a day.
- The calories and macronutrients are **estimates**. A `null` nutrient means at least one confirmed meal that day lacks that estimate. Keep it unknown. Zero is a known value.
- `last_reported_device_sync_at` is the latest successful sync a device reported and can be `null`. `cloud_read_at` is when the server read the summary.
- When the person also shares weight they recorded, `user_logged_weights` is present. Apple Health and Health Connect device records are outside this grant.
- On `401 invalid_connection`, ask the owner to check the connection. A `503 unavailable` can be retried later. The endpoint accepts GET and returns 405 for other methods.

The full request and response types are in the [OpenAPI description](openapi.json). The [fictional response](examples/sample-week.json) includes a missing day and an unknown fat estimate.

## Run the checks

```sh
python3 -m unittest discover -s tests
```
