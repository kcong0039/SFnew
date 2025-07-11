// frontend/src/lib/api.js

export async function fetchScanResult(orderNumber) {
  const response = await fetch(`/api/scan-result/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ barcode: orderNumber }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || "Failed to fetch scan data");
  }

  return response.json();
}