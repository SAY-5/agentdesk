import json

from agentdesk import cli


def test_cli_prints_one_line_per_sample(capsys):
    cli.main()
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) >= 1
    first = json.loads(out[0])
    assert "status" in first
    assert "confidence" in first
