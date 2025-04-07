"use client"

import { useFormContext } from "react-hook-form"
import AsyncSelect from "react-select/async"
import { FormControl, FormField, FormItem, FormLabel } from "./form"
import { cn } from "@/lib/utils"
import { useCallback } from "react"
import debounce from "lodash/debounce"

interface ComboboxFieldProps<T extends {}> {
    name: string
    label: string
    onSearch: (term: string) => Promise<T[]>
    onSelect?: (option: T | null) => void
    getOptionLabel: (option: T) => string
    getOptionValue: (option: T) => string
    disabled?: boolean
    placeholder?: string
    value?: T | null
    showAllOptions?: boolean
    isClearable?: boolean
    menuIsOpen?: boolean
    onFocus?: () => void
    onBlur?: () => void
    defaultOptions?: boolean | T[] // Adicionado suporte para array de opções
    minInputLength?: number
}

export function ComboboxField<T extends {}>({
    name,
    label,
    onSearch,
    onSelect,
    getOptionLabel,
    getOptionValue,
    disabled,
    placeholder = "Selecione...",
    value,
    showAllOptions = false,
    isClearable = false,
    menuIsOpen,
    onFocus,
    onBlur,
    defaultOptions = false,
    minInputLength = 2
}: ComboboxFieldProps<T>) {
    const form = useFormContext();

    // Implementar debounce para evitar muitas requisições
    // eslint-disable-next-line react-hooks/exhaustive-deps
    const debouncedLoadOptions = useCallback(
        debounce(async (inputValue: string, callback: (options: any[]) => void) => {
            if (inputValue.length < minInputLength && !showAllOptions) {
                callback([]);
                return;
            }

            try {
                const results = await onSearch(inputValue);
                const options = results.map(option => ({
                    label: getOptionLabel(option),
                    value: getOptionValue(option),
                    data: option
                }));
                callback(options);
            } catch (error) {
                console.error('Erro na busca:', error);
                callback([]);
            }
        }, 300),
        [onSearch, getOptionLabel, getOptionValue, minInputLength, showAllOptions]
    );

    const loadOptions = (inputValue: string, callback: (options: any[]) => void) => {
        debouncedLoadOptions(inputValue, callback);
    };

    // Converter arrays de defaultOptions para o formato esperado pelo AsyncSelect
    const formattedDefaultOptions = Array.isArray(defaultOptions) 
        ? defaultOptions.map(option => ({
            label: getOptionLabel(option),
            value: getOptionValue(option),
            data: option
        }))
        : defaultOptions;

    return (
        <FormField
            control={form.control}
            name={name}
            render={({ field }) => (
                <FormItem className="flex flex-col">
                    <FormLabel>{label}</FormLabel>
                    <FormControl>
                        <AsyncSelect<{ label: string; value: string; data: T }>
                            isDisabled={disabled}
                            placeholder={placeholder}
                            className="react-select-container"
                            classNamePrefix="react-select"
                            styles={{
                                control: (base) => ({
                                    ...base,
                                    fontSize: '0.875rem',
                                }),
                                menu: (base) => ({
                                    ...base,
                                    fontSize: '0.875rem',
                                }),
                            }}
                            loadOptions={loadOptions}
                            defaultOptions={formattedDefaultOptions || showAllOptions}
                            value={value ? {
                                label: getOptionLabel(value),
                                value: getOptionValue(value),
                                data: value
                            } : null}
                            onChange={(selected) => {
                                if (onSelect) {
                                    onSelect(selected?.data || null);
                                }
                            }}
                            isClearable={isClearable}
                            menuIsOpen={menuIsOpen}
                            noOptionsMessage={({ inputValue }) => 
                                inputValue.length < minInputLength && !showAllOptions
                                    ? `Digite pelo menos ${minInputLength} caracteres para buscar`
                                    : "Nenhum resultado encontrado"
                            }
                            loadingMessage={() => "Carregando..."}
                            onFocus={onFocus}
                            onBlur={onBlur}
                            filterOption={(option, inputValue) => {
                                // Permitir que o componente faça a filtragem no lado do cliente também
                                if (!inputValue) return true;
                                
                                const label = option.label.toLowerCase();
                                const input = inputValue.toLowerCase();
                                
                                // Verificar se o label contém o input (não precisa ser no início)
                                return label.includes(input);
                            }}
                        />
                    </FormControl>
                </FormItem>
            )}
        />
    );
}