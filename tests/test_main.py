from metaphysics_app.main import main


def test_main_version(capsys):
    assert main(["--version"]) == 0

    assert "0.1.0" in capsys.readouterr().out


def test_main_smoke(capsys):
    assert main(["--smoke"]) == 0

    output = capsys.readouterr().out
    assert "algorithm=bazi-core-v0.2" in output
    assert "甲辰" in output
