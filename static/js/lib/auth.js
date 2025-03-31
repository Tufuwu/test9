// @flow
import "isomorphic-fetch"

export const refreshAuthToken = () => {
  return fetch("/api/v0/discussions_token/", { credentials: "include" })
}

export const fetchJSONWithAuthToken = async (url: string) => {
  let response = await fetch(url, { credentials: "include" })

  if (response.status === 401) {
    await refreshAuthToken()
    response = await fetch(url, { credentials: "include" })
  }

  if (response.status < 200 || response.status >= 300) {
    return Promise.reject()
  }
  return response.json()
}
