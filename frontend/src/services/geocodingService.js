const geocodingService = {
  async reverse(latitude, longitude) {
    const params = new URLSearchParams({
      format: "jsonv2",
      lat: String(latitude),
      lon: String(longitude),
      addressdetails: "1",
      zoom: "18",
    });
    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?${params}`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) throw new Error("Address lookup failed.");

    const result = await response.json();
    const address = result.address;
    if (!address) throw new Error("No address was found for this location.");

    const street = address.road || address.pedestrian || address.path || address.residential || "";
    const areaNames = [address.neighbourhood, address.suburb, address.city_district]
      .filter((name, index, names) => name && name !== address.city && names.indexOf(name) === index);

    return {
      address_line1: [address.house_number, street].filter(Boolean).join(" ") || address.neighbourhood || address.suburb || "",
      address_line2: areaNames.join(", "),
      city: address.city || address.town || address.village || address.municipality || address.county || "",
      state: address.state || address.state_district || address.region || "",
      postal_code: address.postcode || "",
      country: address.country || "India",
    };
  },
};

export default geocodingService;