# Enterprise Inventory - React Frontend

This is the frontend component of the Full Stack Developer Technical Assessment, providing a modern, data-heavy Enterprise Inventory Management interface.

## 1. Setup Instructions
Ensure you have **Node.js** (v18+) installed.
1. Open your terminal and navigate to the `frontend` directory.
2. Install the required Node packages:
   ```bash
   npm install
   ```

## 2. How to Run the Application
Start the Vite development server:
```bash
npm run dev
```
The application will be accessible at `http://localhost:5173`. 
*(Note: Ensure the Python FastAPI backend is running simultaneously on `localhost:8000` for the GraphQL API to resolve).*

## 3. How to Run Tests
_No formal test suite (like Vitest or Jest) was mandated or configured for the frontend in this rapid-development iteration._ 
To ensure type safety and build integrity, you can run the TypeScript compiler and linting:
```bash
npm run build
npm run lint
```

## 4. Architecture Overview
- **Core Framework:** React 19 bundled with **Vite** for incredibly fast HMR (Hot Module Replacement) and optimized production builds.
- **Language:** TypeScript for strict type-checking and interface definitions.
- **API Communication:** **Apollo Client** (`@apollo/client/react`) is used to seamlessly interact with the Python Strawberry GraphQL endpoint. It manages complex state caching and supports `apollo-upload-client` for Multipart Form CSV bulk uploads.
- **UI Component Library:** **Mantine UI** (`@mantine/core`). Selected for its enterprise-grade aesthetics, out-of-the-box dark mode support, and data-dense Table implementations.
- **Data Visualization:** **Recharts**. Chosen for its React-native hybrid approach (built on D3). It scales beautifully for data aggregations without the heavy canvas boilerplate of ECharts.

## 5. Assumptions Made
- **Dashboard Usage:** I assumed that users looking at the Analytics charts are okay with client-side aggregations for the current data scale (fetching a large chunk of inventory and grouping them by React `reduce` logic).
- **Design Language:** Assumed an enterprise-focused Dark Mode aesthetic fits best for long-session data entry and monitoring (defaulted tightly in Mantine UI).
- **Apollo Setup:** Assumed `network-only` fetch policies for the main inventory grids so that bulk CSV updates consistently reflect actual server parity immediately after uploads.

## 6. Tradeoffs or Limitations
- **Client-Side Analytics Calculation:** Currently, the `Analytics.tsx` page fetches up to 500 rows and executes the pie/bar chart aggregations via JavaScript on the browser. For millions of rows, this would freeze the browser tab.
- **Form/Error Granularity:** The specific CSV validation errors are dumped into a scrollable alert box instead of a dedicated "Error Resolution Data-Grid".
- **Pagination Strategy:** Pagination is strictly Offset/Limit based. This works well for our scale, but Cursor-based pagination might be required for highly concurrent real-time data environments.

## 7. Improvements With More Time
- **Vitest & React Testing Library:** Implement a robust Unit and Integration testing suite for the React components, specifically mocking the Apollo Provider to test the UI's reaction to GraphQL query failures.
- **E2E Testing:** Add Cypress or Playwright to automate the CSV upload interaction flow.
- **Server-Side Chart Aggregation:** Move the Reducer logics (`Item count by Warehouse`, `Distribution by category`) to the Python Backend and expose them as new GraphQL queries (e.g., `getWarehouseStats`) to save client memory.
- **Caching Optimizations:** Refine Apollo Cache eviction and update policies so we don't need to aggressively use `network-only` configurations.
