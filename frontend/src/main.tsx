import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import { ApolloProvider } from '@apollo/client/react';
import { client } from './graphql/client';
import App from './App';

import '@mantine/core/styles.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ApolloProvider client={client}>
      <MantineProvider defaultColorScheme="dark">
        <App />
      </MantineProvider>
    </ApolloProvider>
  </StrictMode>
);
