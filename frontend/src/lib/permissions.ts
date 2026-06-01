// Mirror of the backend RBAC check so the UI can hide what a user can't do.
export function hasPerm(permissions: string[] | undefined, code: string): boolean {
  if (!permissions) return false;
  if (permissions.includes("*")) return true;
  const module = code.split(".")[0];
  return permissions.includes(code) || permissions.includes(`${module}.*`);
}

export function canViewModule(permissions: string[] | undefined, module: string) {
  return hasPerm(permissions, `${module}.view`);
}
