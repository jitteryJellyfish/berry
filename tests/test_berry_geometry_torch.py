from types import SimpleNamespace

import numpy as np
import pytest
import torch

import berry.berry_geometry_torch as geometry
from berry.utils.logger import log as berry_log


@pytest.fixture
def metadata(monkeypatch):
    value = SimpleNamespace(
        dimensions=2,
        nkx=4,
        nky=3,
        nkz=1,
        nr=16,
        step=0.1,
        noncolin=False,
        data_dir=".",
        geometry_dir=".",
        refname="test",
    )
    monkeypatch.setattr(geometry, "m", value, raising=False)
    return value


def test_module_uses_repository_logger():
    assert geometry.log is berry_log


@pytest.mark.parametrize(
    ("device_available", "mps_available", "expected"),
    [
        (True, True, "cuda"),
        (False, True, "mps"),
        (False, False, "cpu"),
    ],
)
def test_torch_device_selection(monkeypatch, device_available, mps_available, expected):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: device_available)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: mps_available)

    assert geometry._torch_device().type == expected


def test_parse_props_accepts_aliases_and_rejects_unknown():
    assert geometry._parse_props("both,chern_bp") == {"both", "chern_bp"}
    assert geometry._parse_props("chern_all") == {"chern", "chern_curl", "chern_bp", "chern_bp_bz"}
    assert geometry._parse_props("all") == {"both", "chern", "chern_curl", "chern_bp", "chern_bp_bz"}

    with pytest.raises(ValueError, match="invalid property"):
        geometry._parse_props("invalid")


def test_tensor_save_and_load_round_trip(tmp_path):
    path = tmp_path / "tensor.npy"
    original = torch.tensor([[1.0 + 2.0j, 3.0 - 1.0j]], dtype=torch.complex128)

    geometry._save_tensor(path, original)
    loaded = geometry._load_tensor(path)

    assert loaded.dtype == geometry.DTYPE
    assert torch.allclose(loaded.cpu(), original.to(dtype=geometry.DTYPE).cpu())


def test_tile_gradient_uses_finite_difference(metadata):
    metadata.dimensions = 2
    metadata.step = 1.0
    kshape = (4, 3)
    real_dtype = torch.float32 if geometry.DEVICE.type == "mps" else torch.float64
    source = torch.tensor(
        np.arange(12),
        dtype=real_dtype,
        device=geometry.DEVICE,
    ).reshape(kshape + (1,))
    source = source.repeat(1, 1, 1, 2)
    source = source.reshape(12, 1, 2).to(dtype=geometry.DTYPE)

    gradient = geometry._tile_gradient(source, kshape)

    assert gradient.shape == (2, 12, 1, 2)
    assert gradient.dtype == geometry.DTYPE


def test_inpaint_periodic_replaces_mask_with_neighbor_average(metadata):
    arr = torch.ones((3, 3), dtype=geometry.DTYPE, device=geometry.DEVICE)
    mask = torch.zeros((3, 3), dtype=torch.bool, device=geometry.DEVICE)
    mask[1, 1] = True

    result = geometry._inpaint_periodic(arr, mask)

    assert result.shape == arr.shape
    assert torch.allclose(result, arr)
    assert geometry._inpaint_periodic(arr, None) is arr


def test_chern_number_2d(metadata):
    metadata.dimensions = 2
    metadata.step = 0.1
    curvature = torch.ones((2, 3), dtype=geometry.DTYPE, device=geometry.DEVICE)

    result = geometry.chern_number(curvature)

    assert torch.is_tensor(result)
    assert torch.allclose(
        result.cpu(),
        torch.tensor(6 * 0.01 / (2 * torch.pi), dtype=geometry.DTYPE),
    )


def test_chern_number_bp_and_bz_use_tensors(metadata):
    metadata.dimensions = 2
    metadata.nkx = 3
    metadata.nky = 3
    metadata.nr = 16
    pos = torch.ones((16, 3, 3), dtype=geometry.DTYPE, device=geometry.DEVICE)

    assert geometry.berry_phase(pos, 0, 0).item() == pytest.approx(0.0)
    assert geometry.chern_number_bp(pos).item() == pytest.approx(0.0)
    assert geometry.chern_number_bp_bz(pos).item() == pytest.approx(0.0)


def test_geometry_files_complete(tmp_path, metadata):
    metadata.geometry_dir = str(tmp_path)
    bands = [0, 1]

    class DummyLogger:
        def debug(self, message):
            pass

    assert geometry._geometry_files_complete(bands, "conn", DummyLogger()) is False

    for a in bands:
        for b in bands:
            np.save(tmp_path / f"berryConn{a}_{b}.npy", np.zeros((2, 2, 2)))

    assert geometry._geometry_files_complete(bands, "conn", DummyLogger()) is True
