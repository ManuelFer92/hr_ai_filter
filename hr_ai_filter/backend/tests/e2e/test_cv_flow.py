from pathlib import Path

def test_upload_cv_pdf(client):
    pdf_path = Path(__file__).parent.parent / "test_cvs" / "CV_DevOps.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        resp = client.post(
            "/cv/upload",
            files={"file": ("CV_DevOps.pdf", f, "application/pdf")}
        )

    assert resp.status_code == 200
    body = resp.json()

    assert body["filename"] == "CV_DevOps.pdf"
    assert "text" in body
    assert body["text"] != ""
    assert "saved_to" in body


def test_list_cvs(client):
    resp = client.get("/cv/list")
    assert resp.status_code == 200

    data = resp.json()
    assert "count" in data
    assert "cvs" in data
