import io
import app as datapulse


def test_home_page():
    client = datapulse.app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_dashboard_page():
    client = datapulse.app.test_client()
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_invalid_file_upload():
    client = datapulse.app.test_client()

    response = client.post(
        "/upload",
        data={
            "dataset": (
                io.BytesIO(b"test content"),
                "sample.cpp"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Please upload a CSV or Excel file." in response.data


def test_successful_csv_upload(monkeypatch, tmp_path):
    client = datapulse.app.test_client()

    monkeypatch.setattr(datapulse, "UPLOAD_FOLDER", str(tmp_path))
    monkeypatch.setattr(datapulse, "save_dataset", lambda *args: None)

    response = client.post(
        "/upload",
        data={
            "dataset": (
                io.BytesIO(b"Order_ID,Revenue\n1,100\n2,200\n"),
                "test_data.csv"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Dataset uploaded successfully!" in response.data


def test_main_feature_pages():
    client = datapulse.app.test_client()

    routes = [
        "/analytics",
        "/cleaning",
        "/visualization",
        "/insights",
        "/visualquery",
        "/comparison",
        "/reports",
        "/history"
    ]

    for route in routes:
        response = client.get(route, follow_redirects=True)
        assert response.status_code == 200, f"Page failed: {route}"


def test_empty_csv_upload(monkeypatch, tmp_path):
    client = datapulse.app.test_client()
    monkeypatch.setattr(datapulse, "UPLOAD_FOLDER", str(tmp_path))

    response = client.post(
        "/upload",
        data={
            "dataset": (io.BytesIO(b""), "empty.csv")
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Upload failed." in response.data
    assert list(tmp_path.iterdir()) == []


def test_corrupted_excel_upload(monkeypatch, tmp_path):
    client = datapulse.app.test_client()
    monkeypatch.setattr(datapulse, "UPLOAD_FOLDER", str(tmp_path))

    response = client.post(
        "/upload",
        data={
            "dataset": (
                io.BytesIO(b"This is not a valid Excel file"),
                "corrupted.xlsx"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Upload failed." in response.data
    assert list(tmp_path.iterdir()) == []


def test_missing_file_upload():
    client = datapulse.app.test_client()

    response = client.post(
        "/upload",
        data={},
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"No file selected." in response.data


def test_file_size_limit(monkeypatch):
    client = datapulse.app.test_client()

    monkeypatch.setitem(
        datapulse.app.config,
        "MAX_CONTENT_LENGTH",
        1
    )

    response = client.post(
        "/upload",
        data={
            "dataset": (
                io.BytesIO(b"This file is larger than one byte"),
                "large.csv"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"File is too large." in response.data