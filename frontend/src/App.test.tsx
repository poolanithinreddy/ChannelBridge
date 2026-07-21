import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, describe, expect, it } from "vitest";
import App from "./App";
afterEach(() => localStorage.clear());
describe("ChannelBridge", () => {
  it("shows demo authentication choices", () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <MemoryRouter initialEntries={["/login"]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>,
    );
    expect(
      screen.getByRole("heading", { name: /sign in to the demo/i }),
    ).toBeInTheDocument();
    expect(screen.getByText("Partner admin")).toBeInTheDocument();
  });
});
