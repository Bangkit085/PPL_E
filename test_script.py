def test_index_contains_data():
    with open("index.html", "r") as f:
        content = f.read()
    assert "Bangkit Rizky Lillah" in content
    assert "23-085" in content
    assert "<html>" in content
