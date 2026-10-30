import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404


def serve_next_frontend(request, path=""):
    frontend_build_dir = Path(settings.FRONTEND_BUILD_DIR).resolve()
    requested_path = (frontend_build_dir / path).resolve()
    response_status = 200

    if frontend_build_dir not in requested_path.parents and requested_path != frontend_build_dir:
        raise Http404("Frontend asset not found")

    if requested_path.is_dir():
        requested_path = requested_path / "index.html"
    elif not requested_path.exists():
        html_path = requested_path.with_suffix("") / "index.html"
        if html_path.exists():
            requested_path = html_path
        else:
            requested_path = frontend_build_dir / '404.html'
            response_status = 404

    requested_path = requested_path.resolve()
    if frontend_build_dir not in requested_path.parents:
        raise Http404("Frontend asset not found")

    if not requested_path.exists() or not requested_path.is_file():
        raise Http404("Frontend build not found. Run `npm run build` inside ui first.")

    content_type, _ = mimetypes.guess_type(requested_path)
    return FileResponse(open(requested_path, "rb"), content_type=content_type, status=response_status)
