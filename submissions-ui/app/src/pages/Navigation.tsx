import React, { useState } from "react";
import { withRouter, useHistory } from "react-router-dom";
import { Container, Navbar, Nav } from 'react-bootstrap';
import { useAuth } from '../contexts/auth.context';
import { authLogout } from '../services/auth/authService';
import {
  setTokenToLocalStorage,
  setUserToLocalStorage,
  tokenHasExpired
} from '../services/localStorage/localStorageService';

interface NavigationProps {
  location: {pathname: string};
}

interface Environment {
  environment: string | undefined;
}

const assumeProduction = (): string => {
  console.log("Error fetching environment. Assuming production.");
  return "production";
}

const fetchEnvironment = (): Promise<string> => {
  return fetch('/api/v1/environment')
      .then(res => {
          if (res.ok) {
              return res.json() as Promise<Environment>;
          }
          return null;
      })
      .then((res: Environment | null) => {
          if (!res?.environment) {
            return assumeProduction();
          }
          return res.environment;
      })
      .catch((err: any) => {
        return assumeProduction();
      });
}

const getBackgroundClass = (environment: string): string => {
  switch (environment) {
    case "dev":
      return "bg-warning"
    case "test":
      return "bg-info"
    case "staging":
      return "bg-success";
  }
  return "";
}

function Navigation(props: NavigationProps) {
  const { token, setToken, user, setUser } = useAuth();
  const history = useHistory();
  const [environment, setEnvironment] = useState("");
  React.useEffect(() => {
    fetchEnvironment()
    .then((fetchedEnvironment: string) => {
      setEnvironment(fetchedEnvironment);
    });
  }, []);

  const isProduction = () => {
    return environment === "production";
  }

  const logout = function() {
    authLogout().finally(() => {
      setTokenToLocalStorage('');
      setUserToLocalStorage(null);
      setToken('');
      setUser(null);
      history.replace("/");
    })
  }

    return (
    <div className="navigation">
      <Navbar
        className={
          (isProduction() && environment ?
            "navbar-dark" :
            "navbar-light " + getBackgroundClass(environment))
          + " navbar-custom fixed-top"
        }
        expand="lg"
      >
        <Container>
          <Navbar.Brand href="/">
            Submissions
            {environment && !isProduction() &&
              "-" + environment
            }
          </Navbar.Brand>
          { /*
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="ml-auto">
              <Nav.Link href="/search">
                Search
              </Nav.Link>
              {(!token || tokenHasExpired(token)) &&
                <Nav.Link className="nav-link" href="/login">
                  Login
                </Nav.Link>
              }
              {token && !tokenHasExpired(token) &&
                <Nav.Link onClick={logout} className="nav-link" href="/">
                  Logout
                </Nav.Link>
              }
            </Nav>
          </Navbar.Collapse>
            */ }
        </Container>
      </Navbar>
    </div>
  );
}

export default withRouter(Navigation);