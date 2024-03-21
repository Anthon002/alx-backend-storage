-- Calculate the total number of fans for each country of origin of the bands
SELECT origin AS country_origin, SUM(fans) AS total_fans
FROM metal_bands
GROUP BY country_origin
ORDER BY total_fans DESC;
