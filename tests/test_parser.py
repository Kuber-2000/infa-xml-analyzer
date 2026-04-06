"""Tests for infa_xml_analyzer parser."""

from pathlib import Path

import pytest
from lxml import etree

from infa_xml_analyzer.parser import parse_xml, scan_directory, ParseResult

SAMPLE_XML = Path(__file__).parent.parent / "examples" / "sample_export.xml"
MALFORMED_XML = Path(__file__).parent.parent / "examples" / "malformed.xml"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


class TestParseXml:
    """Tests for parse_xml function."""

    def test_extracts_all_folders(self) -> None:
        result = parse_xml(SAMPLE_XML)
        folder_names = [f.name for f in result.folders]
        assert sorted(folder_names) == ["ETL_Finance", "ETL_HR", "ETL_Sales"]

    def test_extracts_mappings_with_correct_counts(self) -> None:
        result = parse_xml(SAMPLE_XML)
        assert len(result.mappings) == 4
        mapping_names = [m.name for m in result.mappings]
        assert "m_Load_Dim_Account" in mapping_names
        assert "m_Load_Fact_Journal" in mapping_names
        assert "m_Load_Fact_Orders" in mapping_names
        assert "m_Load_Dim_Employee" in mapping_names

    def test_extracts_mapplets(self) -> None:
        result = parse_xml(SAMPLE_XML)
        assert len(result.mapplets) == 3
        mapplet_names = [m.name for m in result.mapplets]
        assert "mplt_Currency_Convert" in mapplet_names
        assert "mplt_Date_Dimension" in mapplet_names
        assert "mplt_SCD_Type2" in mapplet_names

    def test_folder_to_mapping_count(self) -> None:
        result = parse_xml(SAMPLE_XML)
        counts = result.folder_to_mapping_count
        assert counts["ETL_Finance"] == 2
        assert counts["ETL_Sales"] == 1
        assert counts["ETL_HR"] == 1

    def test_folder_to_mapplet_count(self) -> None:
        result = parse_xml(SAMPLE_XML)
        counts = result.folder_to_mapplet_count
        assert counts["ETL_Finance"] == 1
        assert counts["ETL_Sales"] == 2
        assert "ETL_HR" not in counts

    def test_lineage_extraction(self) -> None:
        result = parse_xml(SAMPLE_XML)
        assert len(result.lineage) > 0
        # m_Load_Fact_Orders has 1 source and 2 targets -> 2 lineage entries
        orders_lineage = [e for e in result.lineage if e.mapping == "m_Load_Fact_Orders"]
        assert len(orders_lineage) == 2
        targets = {e.target for e in orders_lineage}
        assert targets == {"TGT_FACT_ORDERS", "TGT_DIM_PRODUCT"}

    def test_transformation_path_captured(self) -> None:
        result = parse_xml(SAMPLE_XML)
        account_lineage = [e for e in result.lineage if e.mapping == "m_Load_Dim_Account"]
        assert len(account_lineage) == 1
        assert "EXP_Account_Transform" in account_lineage[0].transformation_path
        assert "LKP_Account_Type" in account_lineage[0].transformation_path

    def test_malformed_xml_raises_error(self) -> None:
        with pytest.raises(etree.XMLSyntaxError):
            parse_xml(MALFORMED_XML)

    def test_file_not_found_raises_error(self) -> None:
        with pytest.raises(FileNotFoundError):
            parse_xml("/nonexistent/path.xml")


class TestScanDirectory:
    """Tests for scan_directory function."""

    def test_scan_finds_xml_files(self) -> None:
        result = scan_directory(EXAMPLES_DIR)
        # Should parse the valid file; malformed gets skipped with warning
        assert len(result.folders) >= 3

    def test_scan_nonexistent_directory(self) -> None:
        with pytest.raises(FileNotFoundError):
            scan_directory("/nonexistent/directory")


class TestParseResult:
    """Tests for ParseResult."""

    def test_merge_combines_results(self) -> None:
        r1 = parse_xml(SAMPLE_XML)
        r2 = parse_xml(SAMPLE_XML)
        original_count = len(r1.mappings)
        r1.merge(r2)
        assert len(r1.mappings) == original_count * 2
