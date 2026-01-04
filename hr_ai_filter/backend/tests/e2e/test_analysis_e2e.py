from pathlib import Path

def test_full_cv_analysis(client):
    payload = {
        "provider": "gemini",
        "model": "gemini-2.5-flash"
    }

    resp = client.post("/llm/switch", json=payload)
    assert resp.status_code == 200

    jobs_resp = client.get("/jobs/list")
    jobs = jobs_resp.json()["jobs"]
    assert jobs, "No hay jobs cargados para test"

    file_name = 'CV_DevOps.pdf'
    pdf_path = Path(__file__).parent.parent / "test_cvs" / f'{file_name}'

    with open(pdf_path, "rb") as f:
        resp = client.post(
            "/cv/upload",
            files={"file": ("CV_DevOps.pdf", f, "application/pdf")}
        )

    assert resp.status_code == 200
    cv_body = resp.json()

    job = None
    for jobItem in jobs:
        if jobItem['filename'] == 'Ingeniero_DevOps.pdf':
            job = jobItem
            break

    payload = {
        "cv_text": cv_body['text'],
        "job_text": job["text"],
        "job_name": job["job_name"],
        "cv_filename": file_name
    }

    resp = client.post("/jobs/analyze", json=payload)
    assert resp.status_code == 200

    data = resp.json()

    assert data["score_final"] >= 75
    assert isinstance(data["resumen"], str)
    assert isinstance(data["fortalezas"], list)
    assert isinstance(data["debilidades"], list)
    assert data["llm_evaluation_score"] >= 4
