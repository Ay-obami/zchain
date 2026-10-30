# zchain — Zcash Chain-Info CLI

A dependency-free Python 3 CLI that queries the actual Z3 regtest Zebra node using JSON-RPC.

## Commands

```bash
./zchain height
# 5

./zchain block 5
# {"height":5,"hash":"5dea2941a078c8598da97b121b8535cf246737a388c2f01f164feb965288f7e5","timestamp":1296688605}

./zchain block invalid
# zchain: error: block height must be a non-negative integer
# exit status: 2
```

- `zchain height` uses `getblockcount` and prints the current height as an integer.
- `zchain block <height>` uses `getblockhash` and `getblock` to return JSON containing the height, block hash, and UNIX timestamp.
- Invalid commands, bad heights, RPC errors, malformed responses, and connection failures produce a clear message on stderr and exit nonzero.

## Z3 regtest setup

```bash
git clone https://github.com/ZcashFoundation/z3.git
cd z3
./scripts/setup-network.sh regtest
docker compose --env-file .env.regtest up -d zebra
curl -sS --user zebra:zebra -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","method":"generate","params":[3],"id":1}' \
  http://127.0.0.1:29232
```

Run `./zchain height` and `./zchain block 3` in this repository.

## RPC environment settings

| Variable | Default | Purpose |
|---|---|---|
| `ZCHAIN_RPC_URL` | `http://127.0.0.1:29232` | Zebra regtest RPC URL |
| `ZCHAIN_RPC_USER` | `zebra` | HTTP Basic username |
| `ZCHAIN_RPC_PASSWORD` | `zebra` | HTTP Basic password |
| `ZCHAIN_RPC_TIMEOUT` | `10` | Seconds before RPC timeout |

Example:

```bash
ZCHAIN_RPC_URL=http://127.0.0.1:29232 ZCHAIN_RPC_USER=zebra ZCHAIN_RPC_PASSWORD=zebra ./zchain height
```

The default credentials are for **local regtest only**. Do not use them on a publicly exposed endpoint.

## Tests and GitHub Actions

```bash
python3 -m unittest discover -s tests -v
```

The [Z3 regtest integration workflow](.github/workflows/z3-regtest.yml) checks out the official Z3 stack, configures and launches a real Zebra Docker service, waits for JSON-RPC, generates three blocks, and tests all three CLI behaviors on every push to main. It also runs unit tests and prints Zebra startup logs on failure.
