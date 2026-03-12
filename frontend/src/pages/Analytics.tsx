import { gql } from '@apollo/client';
import { useQuery } from '@apollo/client/react';
import { Paper, Title, Grid, LoadingOverlay, Text } from '@mantine/core';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';

// Fetch a larger dataset for client-side aggregation
const GET_ALL_ITEMS = gql`
  query GetAllItemsForAnalytics {
    items(limit: 500) {
      category
      warehouse
      quantityOnHand
      stockStatus
    }
  }
`;

const COLORS = [
  '#0088FE',
  '#00C49F',
  '#FFBB28',
  '#FF8042',
  '#8884d8'
];

export default function Analytics() {
  const { data, loading } = useQuery<any>(GET_ALL_ITEMS, { fetchPolicy: 'network-only' });

  // 1. Aggregation: Item count by Warehouse & Low Stock status
  const warehouseAgg = data?.items.reduce((acc: any, item: any) => {
    const w = item.warehouse || 'Unknown';
    if (!acc[w]) {
      acc[w] = { name: w, 'Low Stock': 0, 'In Stock': 0, 'Out of Stock': 0 };
    }
    acc[w][item.stockStatus] += 1;
    return acc;
  }, {});

  const barChartData = warehouseAgg ? Object.values(warehouseAgg) : [];

  // 2. Aggregation: Quantity distribution by Category
  const categoryAgg = data?.items.reduce((acc: any, item: any) => {
    const c = item.category || 'Unknown';
    if (!acc[c]) acc[c] = { name: c, value: 0 };
    acc[c].value += item.quantityOnHand;
    return acc;
  }, {});

  const pieChartData = categoryAgg ? Object.values(categoryAgg) : [];

  return (
    <Paper radius="md" p="md" pos="relative" style={{ minHeight: 400 }}>
      <LoadingOverlay visible={loading} />

      <Title order={4} mb="xl">Inventory Data Visualizations</Title>

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Paper withBorder p="md" radius="md">
            <Title order={5} ta="center" mb="md">Items by Warehouse (Stock Status)</Title>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="In Stock" stackId="a" fill="#82ca9d" />
                <Bar dataKey="Low Stock" stackId="a" fill="#ffc658" />
                <Bar dataKey="Out of Stock" stackId="a" fill="#ff7300" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6 }}>
          <Paper withBorder p="md" radius="md">
            <Title order={5} ta="center" mb="md">Quantity Distribution by Category</Title>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: { name: string; percent?: number }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieChartData.map((_entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <Text ta="center" size="sm" c="dimmed" mt="xs">
              This chart uses Recharts to summarize massive data rapidly based on React architecture.
            </Text>
          </Paper>
        </Grid.Col>
      </Grid>
    </Paper>
  );
}
