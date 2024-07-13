import subprocess
import json

def get_all_disks() -> json:
    # List all disks in the project
    result = subprocess.run(['gcloud', 'compute', 'disks', 'list', '--format=json'], stdout=subprocess.PIPE)
    disks = json.loads(result.stdout)
    return disks

def get_unused_disks(disks) -> list:
    unused_disks: list = []
    for disk in disks:
        if 'users' not in disk:
            disk_info: dict = {
                'name': disk['name'],
                'zone': disk['zone'].split('/')[-1],
                'labels': disk.get('labels', {})
            }
            unused_disks.append(disk_info)
    return unused_disks

def delete_disk(disk_name, zone) -> None:
    # Delete the disk
    subprocess.run(['gcloud', 'compute', 'disks', 'delete', disk_name, '--zone', zone, '--quiet'])

def main() -> None:
    disks: json = get_all_disks()
    unused_disks: list = get_unused_disks(disks)

    print(f"Found {len(unused_disks)} unused disks.")
    for disk in unused_disks:
        print(f"Deleting disk: {disk['name']} in zone: {disk['zone']} with labels: {disk['labels']}")
        delete_disk(disk['name'], disk['zone'])

if __name__ == "__main__":
    main()
