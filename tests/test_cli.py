"""Tests for infa_xml_analyzer CLI commands."""

from pathlib import Path

from click.testing import CliRunner

from infa_xml_analyzer.cli import cli

SAMPLE_XML = str(Path(__file__).parent.parent / "examples" / "sample_export.xml")
MALFORMED_XML = str(Path(__file__).parent.parent / "examples" / "malformed.xml")
EXAMPLES_DIR = str(Path(__file__).parent.parent / "examples")


class TestAnalyzeCommand:
    """Tests for the analyze CLI command."""

    def test_analyze_shows_summary(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", SAMPLE_XML])
        assert result.exit_code == 0
        assert "ETL_Finance" in result.output
        assert "ETL_Sales" in result.output
        assert "ETL_HR" in result.output

    def test_analyze_with_detail_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", SAMPLE_XML, "--detail"])
        assert result.exit_code == 0
        # Rich truncates long names with ellipsis in narrow terminals
        assert "m_Load_Dim_A" in result.output
        assert "m_Load_Fact_" in result.output

    def test_analyze_with_lineage_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", SAMPLE_XML, "--lineage"])
        assert result.exit_code == 0
        assert "SRC_GL_ACCOU" in result.output
        assert "TGT_DIM_ACCO" in result.output

    def test_analyze_nonexistent_file(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "/nonexistent/file.xml"])
        assert result.exit_code != 0

    def test_analyze_malformed_xml(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", MALFORMED_XML])
        assert result.exit_code == 1
        assert "Error" in result.output


class TestScanCommand:
    """Tests for the scan CLI command."""

    def test_scan_directory(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["scan", EXAMPLES_DIR])
        assert result.exit_code == 0
        assert "ETL_Finance" in result.output

    def test_scan_with_detail(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["scan", EXAMPLES_DIR, "--detail"])
        assert result.exit_code == 0
        assert "m_Load_Dim_A" in result.output


class TestExportCommand:
    """Tests for the export CLI command."""

    def test_export_csv(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["export", SAMPLE_XML, "-o", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "summary.csv").exists()
        assert (tmp_path / "mappings.csv").exists()
        assert (tmp_path / "mapplets.csv").exists()
        assert (tmp_path / "lineage.csv").exists()

    def test_export_json(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["export", SAMPLE_XML, "-o", str(tmp_path), "-f", "json"])
        assert result.exit_code == 0
        assert (tmp_path / "analysis.json").exists()

    def test_export_csv_content(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["export", SAMPLE_XML, "-o", str(tmp_path)])
        content = (tmp_path / "summary.csv").read_text()
        assert "ETL_Finance" in content
        assert "Folder,Mappings,Mapplets" in content


class TestVersionFlag:
    """Test CLI version output."""

    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
