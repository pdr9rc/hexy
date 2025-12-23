function clamp(val, min, max) {
  return Math.max(min, Math.min(max, val));
}

export function createHeaderControls(config) {
  const {
    controls = {
      rot: { inputId: "param-rot", valId: "val-rot" },
      tilt: { inputId: "param-tilt", valId: "val-tilt" },
      zoom: { inputId: "param-zoom", valId: "val-zoom" },
      grid: { inputId: "param-grid", valId: "val-grid" },
    },
    resetBtnId = "btn-reset",
    onParamsChange,
    onReset,
    minZoom = 1.0,
    maxZoom = 1.5,
  } = config;

  const uiParams = {
    rot: document.getElementById(controls.rot.inputId),
    tilt: document.getElementById(controls.tilt.inputId),
    zoom: document.getElementById(controls.zoom.inputId),
    grid: document.getElementById(controls.grid.inputId),
  };

  const uiVals = {
    rot: document.getElementById(controls.rot.valId),
    tilt: document.getElementById(controls.tilt.valId),
    zoom: document.getElementById(controls.zoom.valId),
    grid: document.getElementById(controls.grid.valId),
  };

  let currentParams = {
    rot: parseFloat(uiParams.rot?.value || -45),
    tilt: parseFloat(uiParams.tilt?.value || 0.55),
    zoom: clamp(parseFloat(uiParams.zoom?.value || 1.2), minZoom, maxZoom),
    gridAlpha: parseFloat(uiParams.grid?.value || 1),
  };

  function updateValues(params) {
    if (params.rot !== undefined && uiVals.rot) {
      uiVals.rot.textContent = params.rot;
    }
    if (params.tilt !== undefined && uiVals.tilt) {
      uiVals.tilt.textContent = params.tilt.toFixed(2);
    }
    if (params.zoom !== undefined && uiVals.zoom) {
      uiVals.zoom.textContent = params.zoom.toFixed(2);
    }
    if (params.gridAlpha !== undefined && uiVals.grid) {
      uiVals.grid.textContent = params.gridAlpha.toFixed(2);
    }
  }

  function apply() {
    currentParams.rot = parseFloat(uiParams.rot?.value || currentParams.rot);
    currentParams.tilt = parseFloat(uiParams.tilt?.value || currentParams.tilt);
    currentParams.zoom = clamp(parseFloat(uiParams.zoom?.value || currentParams.zoom), minZoom, maxZoom);
    currentParams.gridAlpha = parseFloat(uiParams.grid?.value || currentParams.gridAlpha);

    updateValues(currentParams);

    if (onParamsChange) {
      onParamsChange(currentParams);
    }
  }

  Object.values(uiParams).forEach((el) => {
    if (el) {
      el.addEventListener("input", apply);
    }
  });

  apply();

  const resetBtn = document.getElementById(resetBtnId);
  if (resetBtn && onReset) {
    resetBtn.addEventListener("click", async () => {
      if (resetBtn.disabled) return;
      resetBtn.disabled = true;
      resetBtn.textContent = "REGENERATING...";
      try {
        await onReset();
        resetBtn.textContent = "RESET MAP";
      } catch (error) {
        console.error("Reset failed:", error);
        resetBtn.textContent = "ERROR - RETRY";
        alert(`Failed to regenerate map: ${error.message}`);
      } finally {
        resetBtn.disabled = false;
      }
    });
  }

  return {
    updateValues,
    setParams(params) {
      if (params.rot !== undefined && uiParams.rot) {
        uiParams.rot.value = params.rot;
      }
      if (params.tilt !== undefined && uiParams.tilt) {
        uiParams.tilt.value = params.tilt;
      }
      if (params.zoom !== undefined && uiParams.zoom) {
        uiParams.zoom.value = clamp(params.zoom, minZoom, maxZoom);
      }
      if (params.gridAlpha !== undefined && uiParams.grid) {
        uiParams.grid.value = params.gridAlpha;
      }
      apply();
    },
    getParams() {
      return { ...currentParams };
    },
  };
}
