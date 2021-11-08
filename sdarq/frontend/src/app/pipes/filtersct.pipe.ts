import { Pipe, PipeTransform, Injectable } from '@angular/core';

@Pipe({
    name: 'filtersct',
})
@Injectable()
export class FiltersctPipe implements PipeTransform {
    transform(value: any[], searchString: string): any[] {
        if (!searchString) {
            return value;
        }
        if (searchString) {
            return value.filter((it) => {
                const service = it.service.toLowerCase().includes(searchString.toLowerCase());
                const security_champion = it.security_champion.toLowerCase().includes(searchString.toLowerCase());
                const dev_url = it.dev_url.toLowerCase().includes(searchString.toLowerCase());
                const github = it.github.toLowerCase().includes(searchString.toLowerCase());
                return service + security_champion + dev_url + github;
            });
        }
    }
}
