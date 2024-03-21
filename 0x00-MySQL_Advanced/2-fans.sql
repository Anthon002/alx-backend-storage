--  this will rank the country origins of the bands by fans
SELECT origin AS ori, SUM(fans) AS _fans
FROM metal_bands
GROUP BY ori_
ORDER BY _fans DESC;
