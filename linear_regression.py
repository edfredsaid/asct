import statistics
import math

def calculate_calibration(data_points):
    """Calculates mx+b and R-squared health."""
    if len(data_points) < 20:
        return 1.0, 0.0, 0

    # Outlier rejection (2 Sigma)
    ratios = [p[0] / (p[1] + 0.001) for p in data_points]
    m_r, s_r = statistics.mean(ratios), statistics.stdev(ratios)
    clean = [p for p in data_points if abs((p[0]/(p[1]+0.001)) - m_r) < (2*s_r)]

    n = len(clean)
    if n < 10: return 1.0, 0.0, 0

    x = [p[1] for p in clean]
    y = [p[0] for p in clean]

    sum_x, sum_y = sum(x), sum(y)
    sum_xy = sum(val_x * val_y for val_x, val_y in zip(x, y))
    sum_xx = sum(val_x**2 for val_x in x)
    sum_yy = sum(val_y**2 for val_y in y)

    denom = (n * sum_xx - sum_x**2)
    if denom == 0: return 1.0, 0.0, 0

    m = (n * sum_xy - sum_x * sum_y) / denom
    b = (sum_y - m * sum_x) / n

    # Calculate R-squared (Health)
    num = (n * sum_xy - sum_x * sum_y)**2
    den = (n * sum_xx - sum_x**2) * (n * sum_yy - sum_y**2)
    r_sq = (num / den) if den != 0 else 0

    return round(m, 4), round(b, 4), int(r_sq * 100)
