import { AppShell, Burger, Group, Title, Tabs } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconBox, IconChartBar } from '@tabler/icons-react';
import { useState } from 'react';
import Inventory from './pages/Inventory';
import Analytics from './pages/Analytics';

function App() {
  const [opened, { toggle }] = useDisclosure();
  const [activeTab, setActiveTab] = useState<string | null>('inventory');

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <IconBox size={30} color="royalblue" />
          <Title order={3}>Enterprise Inventory</Title>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Tabs orientation="vertical" value={activeTab} onChange={setActiveTab}>
          <Tabs.List>
            <Tabs.Tab value="inventory" leftSection={<IconBox size={14} />}>
              Inventory List
            </Tabs.Tab>
            <Tabs.Tab value="analytics" leftSection={<IconChartBar size={14} />}>
              Analytics & Insights
            </Tabs.Tab>
          </Tabs.List>
        </Tabs>
      </AppShell.Navbar>

      <AppShell.Main>
        {activeTab === 'inventory' && <Inventory />}
        {activeTab === 'analytics' && <Analytics />}
      </AppShell.Main>
    </AppShell>
  );
}

export default App;
