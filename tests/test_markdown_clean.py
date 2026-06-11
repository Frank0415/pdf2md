from pdf2md.markdown_clean import strip_sup_markup


def test_unwraps_paired_sup_tags():
    raw = "• <sup>Node</sup> <sup>manager</sup> <sup>failure</sup>"
    assert strip_sup_markup(raw) == "• Node manager failure"


def test_removes_orphan_sup_fragments():
    raw = "hello </sup> world <sup> there"
    assert strip_sup_markup(raw) == "hello  world  there"


def test_preserves_non_sup_content():
    raw = "## Title\n\nNormal **bold** text."
    assert strip_sup_markup(raw) == raw
