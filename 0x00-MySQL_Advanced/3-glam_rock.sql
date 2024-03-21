-- Retrieve bands specializing in Glam rock and sort them by their longevity
SELECT band_name AS band_name, IFNULL(split, 2020) - IFNULL(formed, 0) AS longevity
FROM metal_bands
WHERE style LIKE '%Glam rock%'
ORDER BY longevity DESC;
