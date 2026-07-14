package com.orange;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/lines")
public class OrangeController {

    @GetMapping("/{id}")
    public String line(
        @PathVariable String id) {

        return "Orange line " + id;
    }
}