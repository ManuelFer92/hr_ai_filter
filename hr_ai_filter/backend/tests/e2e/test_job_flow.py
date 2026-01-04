def test_list_jobs(client):
    resp = client.get("/jobs/list")
    assert resp.status_code == 200

    data = resp.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)

    if data["jobs"]:
        job = data["jobs"][0]
        assert "job_name" in job
        assert "text" in job
