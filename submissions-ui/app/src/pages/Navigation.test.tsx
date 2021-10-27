import React from 'react';
import { render, screen } from '@testing-library/react';
import Navigation from './Navigation';
import userEvent from '@testing-library/user-event';
import { act } from "react-dom/test-utils";
import { BrowserRouter } from 'react-router-dom';

afterEach(() => {
    // remove the mock to ensure tests are completely isolated
    if (global.fetch.mock) {
        global.fetch.mockRestore();
    }
});

// helper function for ok'ing only matching API requests
const mockFetchOnMatch = (regex: string, obj: object) => {
    jest.spyOn(global, "fetch").mockImplementation((
        input: RequestInfo,
        init?: RequestInit | undefined
    ) => {
        const compiledRegex = RegExp(regex);
        const match = compiledRegex.test(input as string);
        const body = match ? obj : null;

        return Promise.resolve({
            json: () => Promise.resolve(body),
            ok: match
        });
    });
}

test('Confirm no environment indicators on Production', async () => {
    const fakeEnvironment = {
        "environment": "production"
    }

    mockFetchOnMatch("^/api/v1/environment", fakeEnvironment);
    await act(async () => {
        render(<BrowserRouter><Navigation/></BrowserRouter>)
    });

    // check that nothing like "Submissions-dev" is in the navigation bar
    expect(screen.queryAllByText(RegExp("^Submissions\-"))).toHaveLength(0);
});

test('Confirm a non production environment shows indicators', async () => {
    const fakeEnvironment = {
        "environment": "staging"
    }

    mockFetchOnMatch("^/api/v1/environment", fakeEnvironment);
    await act(async () => {
        render(<BrowserRouter><Navigation/></BrowserRouter>)
    });

    // check that "Submissions-staging" is present
    expect(screen.queryAllByText("Submissions-staging")).not.toHaveLength(0);
});
