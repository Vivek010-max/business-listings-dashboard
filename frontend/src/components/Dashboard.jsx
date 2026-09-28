import React, { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import "./dashboard.css";

const API_BASE = "http://localhost:8000";

// The exact "Warm Greyscale" palette
const WARM_WHITE = "#F8F3EC";
const WARM_BLACK = "#3a3a3a";
const WARM_GREY = "#343434";

// Using opacities of the palette to support multiple categories
const CATEGORY_COLORS = {
  Restaurant: WARM_BLACK,
  "IT Services": WARM_GREY,
  Healthcare: "rgba(28, 27, 26, 0.7)",
  Education: "rgba(168, 162, 158, 0.5)",
  "Real Estate": "rgba(19, 17, 15, 0.4)",
};

// Exact 1-to-1 mapping of the three colors for the three sources
const SOURCE_COLORS = {
  "Google Maps": WARM_BLACK,
  Justdial: WARM_GREY,
  Sulekha: WARM_WHITE,
};

const formatNumber = (value) =>
  new Intl.NumberFormat("en-IN").format(value);

const tooltipStyle = {
  backgroundColor: WARM_WHITE,
  border: `1px solid ${WARM_GREY}`,
  borderRadius: "8px",
  boxShadow: "0 8px 20px rgba(28, 27, 26, 0.08)",
  fontSize: "13px",
  color: WARM_BLACK,
  fontFamily: "inherit",
};

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalListings: 0,
    cities: 0,
    categories: 0,
    sources: 0,
  });

  const [cityData, setCityData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [sourceData, setSourceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [cityResponse, categoryResponse, sourceResponse] =
          await Promise.all([
            fetch(`${API_BASE}/dashboard/city`),
            fetch(`${API_BASE}/dashboard/category`),
            fetch(`${API_BASE}/dashboard/source`),
          ]);

        if (
          !cityResponse.ok ||
          !categoryResponse.ok ||
          !sourceResponse.ok
        ) {
          throw new Error("Failed to fetch dashboard data");
        }

        const [cityResult, categoryResult, sourceResult] =
          await Promise.all([
            cityResponse.json(),
            categoryResponse.json(),
            sourceResponse.json(),
          ]);

        const totalListings = cityResult.reduce(
          (sum, item) => sum + item.count,
          0
        );

        setStats({
          totalListings,
          cities: cityResult.length,
          categories: categoryResult.length,
          sources: sourceResult.length,
        });

        setCityData(
          cityResult.map((item) => ({
            city: item.city,
            count: item.count,
          }))
        );

        setCategoryData(
          categoryResult
            .map((item) => ({
              name: item.category,
              count: item.count,
            }))
            .sort((a, b) => b.count - a.count)
        );

        setSourceData(
          sourceResult
            .map((item) => ({
              name: item.source,
              count: item.count,
            }))
            .sort((a, b) => b.count - a.count)
        );
      } catch (err) {
        setError(
          err.message ||
            "Something went wrong connecting to FastAPI."
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const sourceChartData = useMemo(
    () =>
      sourceData.map((item) => ({
        ...item,
        fill: SOURCE_COLORS[item.name] || WARM_GREY,
      })),
    [sourceData]
  );

  const categoryChartData = useMemo(
    () =>
      categoryData.map((item) => ({
        ...item,
        fill: CATEGORY_COLORS[item.name] || WARM_GREY,
      })),
    [categoryData]
  );

  const maxCityValue = useMemo(
    () => Math.max(0, ...cityData.map((item) => item.count)),
    [cityData]
  );

  const cityChartData = useMemo(
    () =>
      cityData.map((item) => ({
        ...item,
        visualCount: Math.sqrt(Math.max(item.count, 1)),
      })),
    [cityData]
  );

  const topCategory = categoryData[0];

  return (
    <div className="dashboard">
      <div className="dashboard-container">

        {/* Header */}
        <header className="topbar">
          <div>
            <h1>Directory Overview</h1>
          </div>
        </header>

        {/* Loading & Error States */}
        {loading && (
          <div className="state-card">
            <div className="loader"></div>
            <span>Fetching data from backend...</span>
          </div>
        )}

        {error && (
          <div className="error-card">
            <strong>Unable to load dashboard</strong>
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && (
          <>
            {/* KPI Section */}
            <section className="stats-grid">

              <div className="stat-card stat-card-primary">
                <div className="stat-top">
                  <span>Total Listings</span>
                  <div className="stat-icon">↗</div>
                </div>

                <div className="stat-value">
                  {formatNumber(stats.totalListings)}
                </div>

                <div className="stat-description">
                  Total ingested records
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-top">
                  <span>Cities Tracked</span>
                  <div className="stat-icon">⌖</div>
                </div>

                <div className="stat-value">
                  {stats.cities}
                </div>

                <div className="stat-description">
                  Different locations
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-top">
                  <span>Categories</span>
                  <div className="stat-icon">▦</div>
                </div>

                <div className="stat-value">
                  {stats.categories}
                </div>

                <div className="stat-description">
                  Business sectors
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-top">
                  <span>Data Sources</span>
                  <div className="stat-icon">◉</div>
                </div>

                <div className="stat-value">
                  {stats.sources}
                </div>

                <div className="stat-description">
                  Integrated directories
                </div>
              </div>

            </section>

            {/* Main Charts */}
            <section className="charts-grid">

              {/* City Breakdown */}
              <div className="chart-card chart-card-large">

                <div className="chart-header">
                  <div>
                    <h2>Listings by City</h2>
                  </div>
                </div>

                <div className="chart-area city-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={cityChartData}
                      margin={{
                        top: 20,
                        right: 15,
                        left: 0,
                        bottom: 10,
                      }}
                    >
                      <CartesianGrid
                        stroke="rgba(168, 162, 158, 0.2)"
                        strokeDasharray="4 4"
                        vertical={false}
                      />

                      <XAxis
                        dataKey="city"
                        axisLine={false}
                        tickLine={false}
                        tick={{
                          fill: WARM_BLACK,
                          fontSize: 13,
                          fontWeight: 500,
                        }}
                        dy={10}
                      />

                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        domain={[
                          0,
                          Math.ceil(Math.sqrt(maxCityValue)) || 1,
                        ]}
                        tickFormatter={(value) =>
                          formatNumber(Math.round(value ** 2))
                        }
                        tick={{
                          fill: WARM_BLACK,
                          fontSize: 13,
                          fontWeight: 500,
                        }}
                        dx={-10}
                      />

                      <Tooltip
                        contentStyle={tooltipStyle}
                        itemStyle={{
                          color: WARM_BLACK,
                          fontWeight: 500,
                        }}
                        cursor={{
                          fill: "rgba(28, 27, 26, 0.04)",
                        }}
                        formatter={(
                          _value,
                          _name,
                          item
                        ) => [
                          formatNumber(
                            item?.payload?.count ?? _value
                          ),
                          "Listings",
                        ]}
                      />

                      <Bar
                        dataKey="visualCount"
                        fill={WARM_BLACK}
                        radius={[4, 4, 4, 4]}
                        maxBarSize={60}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Source Distribution */}
              <div className="chart-card">

                <div className="chart-header">
                  <div>
                    <h2>Single Data source</h2>
                  </div>
                </div>

                <div className="chart-area source-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>

                      <Pie
                        data={sourceChartData}
                        dataKey="count"
                        nameKey="name"
                        innerRadius={65}
                        outerRadius={95}
                        paddingAngle={4}
                        stroke={WARM_BLACK}
                        strokeWidth={2}
                      >
                        {sourceChartData.map((entry) => (
                          <Cell
                            key={entry.name}
                            fill={entry.fill}
                          />
                        ))}
                      </Pie>

                      <Tooltip
                        contentStyle={tooltipStyle}
                        itemStyle={{
                          color: WARM_BLACK,
                          fontWeight: 500,
                        }}
                        formatter={(value) => [
                          formatNumber(value),
                          "Listings",
                        ]}
                      />

                      <Legend
                        verticalAlign="bottom"
                        iconType="circle"
                        wrapperStyle={{
                          fontSize: "13px",
                          paddingTop: "15px",
                        }}
                        formatter={(value) => (
                          <span
                            style={{
                              color: WARM_BLACK,
                              fontWeight: 500,
                            }}
                          >
                            {value}
                          </span>
                        )}
                      />

                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Category Breakdown */}
              <div className="chart-card chart-card-full">

                <div className="chart-header category-header">
                  <div>
                    <h2>Listings by Category</h2>
                  </div>

                  {topCategory && (
                    <div className="highlight-box">
                      <span>Highest Volume</span>
                      <strong>{topCategory.name}</strong>
                    </div>
                  )}
                </div>

                {/* Horizontal category chart */}
                <div
                  className="chart-area category-chart"
                  style={{ height: "650px" }}
                >
                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >
                    <BarChart
                      data={categoryChartData}
                      layout="vertical"
                      margin={{
                        top: 10,
                        right: 45,
                        left: 20,
                        bottom: 10,
                      }}
                    >

                      <CartesianGrid
                        stroke="rgba(168, 162, 158, 0.2)"
                        strokeDasharray="4 4"
                        horizontal={false}
                      />

                      {/* Number axis */}
                      <XAxis
                        type="number"
                        axisLine={false}
                        tickLine={false}
                        tick={{
                          fill: WARM_BLACK,
                          fontSize: 12,
                          fontWeight: 500,
                        }}
                        tickFormatter={(value) =>
                          formatNumber(value)
                        }
                      />

                      {/* Category names */}
                      <YAxis
                        type="category"
                        dataKey="name"
                        axisLine={false}
                        tickLine={false}
                        width={125}
                        tick={{
                          fill: WARM_BLACK,
                          fontSize: 12,
                          fontWeight: 500,
                        }}
                      />

                      <Tooltip
                        contentStyle={tooltipStyle}
                        itemStyle={{
                          color: WARM_BLACK,
                          fontWeight: 500,
                        }}
                        cursor={{
                          fill: "rgba(28, 27, 26, 0.04)",
                        }}
                        formatter={(value) => [
                          formatNumber(value),
                          "Listings",
                        ]}
                      />

                      <Bar
                        dataKey="count"
                        radius={[0, 4, 4, 0]}
                        maxBarSize={24}
                      >
                        {categoryChartData.map((entry) => (
                          <Cell
                            key={entry.name}
                            fill={entry.fill}
                          />
                        ))}
                      </Bar>

                    </BarChart>
                  </ResponsiveContainer>
                </div>

              </div>

            </section>
          </>
        )}

      </div>
    </div>
  );
}