from pdf2md.scan_contrast import contrast_ratio, normalize_color


def test_white_on_purple_slide_has_high_contrast():
    foreground = (0.98, 0.98, 0.98)
    background = (0.45, 0.12, 0.55)
    assert contrast_ratio(foreground, background) >= 3.0


def test_white_on_white_has_low_contrast():
    foreground = (1.0, 1.0, 1.0)
    background = (0.99, 0.99, 0.99)
    assert contrast_ratio(foreground, background) < 1.15


def test_normalize_cmyk():
    assert normalize_color((0.0, 0.0, 0.0, 0.0)) == (1.0, 1.0, 1.0)
