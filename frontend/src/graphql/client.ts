import { ApolloClient, InMemoryCache } from '@apollo/client';
// @ts-ignore
import UploadHttpLink from 'apollo-upload-client/UploadHttpLink.mjs';

const uploadLink = new UploadHttpLink({
  uri: 'http://localhost:8000/graphql',
});

export const client = new ApolloClient({
  link: uploadLink,
  cache: new InMemoryCache(),
});
