import React, { useState } from 'react';
import { gql } from '@apollo/client';
import { useQuery, useMutation } from '@apollo/client/react';
import {
  Table, Select, TextInput, Group, Button, Paper, Badge,
  Pagination, LoadingOverlay, FileButton, Alert, Text, Divider
} from '@mantine/core';
import { IconSearch, IconUpload, IconAlertCircle } from '@tabler/icons-react';

const GET_ITEMS = gql`
  query GetItems(
    $search: String
    $category: String
    $warehouse: String
    $stockStatus: String
    $sortBy: String
    $sortDesc: Boolean
    $skip: Int
    $limit: Int
  ) {
    items(
      search: $search
      category: $category
      warehouse: $warehouse
      stockStatus: $stockStatus
      sortBy: $sortBy
      sortDesc: $sortDesc
      skip: $skip
      limit: $limit
    ) {
      sku
      name
      category
      warehouse
      quantityOnHand
      reorderThreshold
      stockStatus
      lastUpdated
    }
  }
`;

const IMPORT_CSV = gql`
  mutation ImportCSV($file: Upload!) {
    importTransactions(file: $file) {
      totalRows
      acceptedRows
      rejectedRows
      validationErrors
    }
  }
`;

export default function Inventory() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string | null>(null);
  const [warehouse, setWarehouse] = useState<string | null>(null);
  const [stockStatus, setStockStatus] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<string | null>('last_updated');
  const [sortDesc, setSortDesc] = useState<string | null>('true');
  const [page, setPage] = useState(1);
  const limit = 10;
  
  const resetRef = React.useRef<() => void>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  const { data, loading, refetch } = useQuery<any>(GET_ITEMS, {
    variables: {
      search: search || null,
      category,
      warehouse,
      stockStatus,
      sortBy,
      sortDesc: sortDesc === 'true',
      skip: (page - 1) * limit,
      limit,
    },
    fetchPolicy: 'network-only',
  });

  const [importCsv, { loading: uploadLoading }] = useMutation(IMPORT_CSV, {
    onCompleted: (resultData: any) => {
      setUploadResult(resultData.importTransactions);
      refetch();
    },
  });

  const handleFileUpload = (file: File | null) => {
    if (file) {
      importCsv({ variables: { file } });
      resetRef.current?.();
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'In Stock': return 'green';
      case 'Low Stock': return 'yellow';
      case 'Out of Stock': return 'red';
      default: return 'gray';
    }
  };

  return (
    <Paper radius="md" p="md" pos="relative">
      <LoadingOverlay visible={loading || uploadLoading} />
      
      <Group justify="space-between" mb="md">
        <TextInput
          placeholder="Search SKU or Name"
          leftSection={<IconSearch size={16} />}
          value={search}
          onChange={(e) => { setSearch(e.currentTarget.value); setPage(1); }}
          style={{ width: '300px' }}
        />
        
        <Group>
          <FileButton resetRef={resetRef} onChange={handleFileUpload} accept="text/csv">
            {(props) => (
              <Button {...props} loading={uploadLoading} leftSection={<IconUpload size={16} />} color="blue">
                Bulk Import CSV
              </Button>
            )}
          </FileButton>
        </Group>
      </Group>

      {uploadResult && (
        <Alert 
          icon={<IconAlertCircle size={16} />} 
          title="Import Summary" 
          color={uploadResult.rejectedRows > 0 ? "yellow" : "green"} 
          withCloseButton 
          onClose={() => setUploadResult(null)}
          mb="md"
        >
          <Text size="sm">
            Total processed: {uploadResult.totalRows} | 
            Accepted: {uploadResult.acceptedRows} | 
            Rejected: {uploadResult.rejectedRows}
          </Text>
          {uploadResult.validationErrors.length > 0 && (
            <div style={{ marginTop: 10, maxHeight: 100, overflow: 'auto' }}>
              {uploadResult.validationErrors.map((err: string, i: number) => (
                <Text size="xs" c="dimmed" key={i}>• {err}</Text>
              ))}
            </div>
          )}
        </Alert>
      )}

      <Group grow mb="xl">
        <Select
          placeholder="Filter Category"
          data={['Electronics', 'Furniture', 'Clothing']}
          value={category}
          onChange={(v) => { setCategory(v); setPage(1); }}
          clearable
        />
        <Select
          placeholder="Filter Warehouse"
          data={['Jakarta', 'Bandung', 'Surabaya', 'W1', 'W2']}
          value={warehouse}
          onChange={(v) => { setWarehouse(v); setPage(1); }}
          clearable
        />
        <Select
          placeholder="Filter Status"
          data={['In Stock', 'Low Stock', 'Out of Stock']}
          value={stockStatus}
          onChange={(v) => { setStockStatus(v); setPage(1); }}
          clearable
        />
      </Group>

      <Divider my="sm" />
      <Group justify="right" mb="sm">
        <Select
          label="Sort By"
          data={[
            { value: 'name', label: 'Item Name' },
            { value: 'quantity', label: 'Quantity' },
            { value: 'last_updated', label: 'Last Updated' },
          ]}
          value={sortBy}
          onChange={setSortBy}
        />
        <Select
          label="Sort Order"
          data={[
            { value: 'false', label: 'Ascending' },
            { value: 'true', label: 'Descending' }
          ]}
          value={sortDesc}
          onChange={setSortDesc}
        />
      </Group>

      <Table striped highlightOnHover withTableBorder>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>SKU</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Category</Table.Th>
            <Table.Th>Warehouse</Table.Th>
            <Table.Th>Stock</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Last Updated</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {data?.items.length > 0 ? (
            data.items.map((item: any) => (
              <Table.Tr key={item.sku}>
                <Table.Td>{item.sku}</Table.Td>
                <Table.Td fw={500}>{item.name}</Table.Td>
                <Table.Td>{item.category}</Table.Td>
                <Table.Td>{item.warehouse}</Table.Td>
                <Table.Td>{item.quantityOnHand} (Min: {item.reorderThreshold})</Table.Td>
                <Table.Td>
                  <Badge color={getStatusColor(item.stockStatus)} variant="light">
                    {item.stockStatus}
                  </Badge>
                </Table.Td>
                <Table.Td>{new Date(item.lastUpdated).toLocaleDateString()}</Table.Td>
              </Table.Tr>
            ))
          ) : (
            <Table.Tr>
              <Table.Td colSpan={7} ta="center">No items found.</Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>

      <Group justify="center" mt="xl">
        <Pagination value={page} onChange={setPage} total={10} color="royalblue" />
      </Group>
    </Paper>
  );
}
