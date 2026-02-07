# Ansible Patterns

## Project Structure

```
ansible/
├── ansible.cfg
├── inventory/
│   ├── production
│   └── staging
├── group_vars/
│   ├── all.yml
│   └── webservers.yml
├── host_vars/
│   └── web1.yml
├── roles/
│   └── webserver/
│       ├── tasks/
│       │   └── main.yml
│       ├── handlers/
│       │   └── main.yml
│       ├── templates/
│       │   └── nginx.conf.j2
│       ├── files/
│       ├── vars/
│       │   └── main.yml
│       └── defaults/
│           └── main.yml
└── playbooks/
    └── deploy.yml
```

## Playbook Pattern

```yaml
---
- name: Deploy web application
  hosts: webservers
  become: true
  vars:
    app_name: myapp
    app_port: 8080

  pre_tasks:
    - name: Update apt cache
      apt:
        update_cache: true
        cache_valid_time: 3600

  roles:
    - role: common
    - role: webserver
      vars:
        nginx_port: "{{ app_port }}"

  post_tasks:
    - name: Verify deployment
      uri:
        url: "http://localhost:{{ app_port }}/health"
        status_code: 200
```

## Task Best Practices

```yaml
# Use fully qualified module names
- name: Install packages
  ansible.builtin.apt:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - python3

# Idempotent file operations
- name: Create config directory
  ansible.builtin.file:
    path: /etc/myapp
    state: directory
    owner: root
    group: root
    mode: '0755'

# Template with validation
- name: Deploy nginx config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: nginx -t -c %s
  notify: Restart nginx
```

## Handlers

```yaml
# roles/webserver/handlers/main.yml
---
- name: Restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted

- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

## Variables and Defaults

```yaml
# roles/webserver/defaults/main.yml
---
nginx_worker_processes: auto
nginx_worker_connections: 1024
nginx_keepalive_timeout: 65

# roles/webserver/vars/main.yml (higher priority)
---
nginx_package: nginx-full
```

## Conditionals and Loops

```yaml
# Conditional execution
- name: Install Debian packages
  ansible.builtin.apt:
    name: nginx
  when: ansible_os_family == "Debian"

# Loop with index
- name: Create users
  ansible.builtin.user:
    name: "{{ item.name }}"
    uid: "{{ item.uid }}"
  loop:
    - { name: alice, uid: 1001 }
    - { name: bob, uid: 1002 }

# Register and use results
- name: Get service status
  ansible.builtin.command: systemctl status nginx
  register: nginx_status
  changed_when: false
  failed_when: false

- name: Debug status
  ansible.builtin.debug:
    var: nginx_status.stdout_lines
  when: nginx_status.rc != 0
```

## Secrets with Vault

```bash
# Encrypt file
ansible-vault encrypt group_vars/all/vault.yml

# Encrypt string
ansible-vault encrypt_string 'my_secret' --name 'db_password'

# Run with vault
ansible-playbook deploy.yml --ask-vault-pass
ansible-playbook deploy.yml --vault-password-file ~/.vault_pass
```

## Testing with Molecule

```yaml
# molecule/default/molecule.yml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: debian:bullseye
provisioner:
  name: ansible
verifier:
  name: ansible
```

## Linting

```bash
# Run ansible-lint
ansible-lint playbooks/

# Check syntax
ansible-playbook --syntax-check playbooks/deploy.yml

# Dry run
ansible-playbook playbooks/deploy.yml --check --diff
```
