import React from "react";
import { Link, withRouter, useHistory } from "react-router-dom";
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

function Navigation(props: NavigationProps) {
  const { token, setToken, user, setUser } = useAuth();
  const history = useHistory();


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
      <nav className="navbar navbar-expand-lg navbar-dark navbar-custom fixed-top">
        <div className="container">
          <Link className="navbar-brand" to="/">Submissions</Link>
          <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive" aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarResponsive">
            <ul className="navbar-nav ml-auto">
              {(!token || tokenHasExpired(token)) &&
                <li
                  className={`nav-item  ${
                    props.location.pathname === "/login" ? "active" : ""
                  }`}
                >
                  <Link className="nav-link" to="/login">
                    Login
                  </Link>
                </li>
              }
              {token && !tokenHasExpired(token) &&
                <li
                  className="nav-item" 
                >
                    <a onClick={logout} className="nav-link" href="/">Logout</a>
                </li>
              }

            </ul>
          </div>
        </div>
      </nav>
    </div>
  );
}

export default withRouter(Navigation);