"""Unit tests for chain-info CLI."""
import importlib.machinery
import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader("zchain", str(Path(__file__).resolve().parents[1] / "zchain"))
module = importlib.util.module_from_spec(importlib.util.spec_from_loader("zchain", loader))
loader.exec_module(module)
HASH = "a" * 64


class TestCLI(unittest.TestCase):
    def test_height(self):
        with patch.object(module, "rpc", return_value=5) as rpc, redirect_stdout(io.StringIO()) as out:
            self.assertEqual(module.main(["height"]), 0)
        self.assertEqual(out.getvalue(), "5\n")
        rpc.assert_called_once_with("getblockcount", [])

    def test_block(self):
        with patch.object(module, "rpc", side_effect=[HASH, {"hash": HASH, "time": 1296688605}]) as rpc, redirect_stdout(io.StringIO()) as out:
            self.assertEqual(module.main(["block", "5"]), 0)
        self.assertEqual(json.loads(out.getvalue()), {"height": 5, "hash": HASH, "timestamp": 1296688605})
        self.assertEqual(rpc.call_args_list[0].args, ("getblockhash", [5]))
        self.assertEqual(rpc.call_args_list[1].args, ("getblock", [HASH, 1]))

    def test_invalid_arguments(self):
        for args in ([], ["bad"], ["block"], ["block", "NaN"], ["block", "-1"], ["block", "1.2"], ["height", "3"]):
            with self.subTest(args=args), self.assertRaises(ValueError):
                module.main(args)

    def test_rpc_failure(self):
        with patch.object(module, "rpc", side_effect=module.RPCError("RPC error")):
            with self.assertRaisesRegex(module.RPCError, "RPC error"):
                module.main(["block", "999"])

    def test_bad_block_data(self):
        for values in (["short"], [HASH, {"hash": HASH}], [HASH, {"hash": "b" * 64, "time": 1}]):
            with self.subTest(values=values), patch.object(module, "rpc", side_effect=values):
                with self.assertRaises(module.RPCError):
                    module.main(["block", "2"])

    def test_bad_height_data(self):
        with patch.object(module, "rpc", return_value="2"):
            with self.assertRaises(module.RPCError):
                module.main(["height"])


if __name__ == "__main__":
    unittest.main()
